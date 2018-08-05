"""
    Copyright (C) 2017, ContraxSuite, LLC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    You can also be released from the requirements of the license by purchasing
    a commercial license from ContraxSuite, LLC. Buying such a license is 
    mandatory as soon as you develop commercial activities involving ContraxSuite 
    software without disclosing the source code of your own applications.  These 
    activities include: offering paid services to customers as an ASP or "cloud"
    provider, processing documents on the fly in a web application, 
    or shipping ContraxSuite within a closed source product.
"""

# Celery imports
from celery import shared_task

# Project imports
from apps.celery import app
from apps.document.models import Document, TextUnit
from apps.employee.models import Employee, Employer, Provision
from apps.employee.services import get_employee_name, get_employer_name, get_salary, \
    get_effective_date, get_similar_to_non_compete, get_similar_to_termination, \
    get_vacation_duration, get_governing_geo, get_similar_to_benefits, \
    is_employment_doc, get_similar_to_severance
from apps.task.tasks import BaseTask, ExtendedTask
from apps.task.utils.text.segment import segment_sentences

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.2/LICENSE"
__version__ = "1.1.2"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class LocateEmployees(BaseTask):
    """
        Locate Employees, i.e. extract employee objects
        from uploaded employment agreement documents files in a given directory
        :param kwargs
        :return:
    """
    name = 'Locate Employees'

    def process(self, **kwargs):
        """
        Locate employees
        :param kwargs:
        :return:
        """
        if kwargs.get('delete'):
            deleted = Employee.objects.all().delete() + Employer.objects.all().delete() + Provision.objects.all().delete()
            self.log_info('Deleted: ' + str(deleted))

        documents = Document.objects.all()
        # TODO: outdated
        if kwargs.get('document_type'):
            documents = documents.filter(document_type__in=kwargs['document_type'])
            self.log_info(
                'Filter documents by "%s" document type.' % str(kwargs['document_type']))

        if kwargs.get('document_id'):
            documents = documents.filter(pk=kwargs['document_id'])
            self.log_info('Process document id={}.'.format(kwargs['document_id']))

        self.log_info(
            'Found {0} Documents. Added {0} subtasks.'.format(documents.count()))

        parse_document_for_employee_args = []
        for d in documents:
            parse_document_for_employee_args.append((d.id,
                                                     kwargs.get('no_detect', True)))

        self.run_sub_tasks('Locate Employees for Each Document',
                           LocateEmployees.parse_document_for_employee,
                           parse_document_for_employee_args)

    @staticmethod
    @shared_task(base=ExtendedTask, bind=True)
    def parse_document_for_employee(task: ExtendedTask, document_id: int, no_detect: bool):
        detect = not no_detect
        document = Document.objects.get(pk=document_id)

        task.log_info('Process employment document: #{}. {}'.format(
            document_id, document.name))

        if detect and not is_employment_doc(document.full_text or document.text):
            task.log_info('Not an employment document: #{}. {}'.format(
                document_id, document.name))
            return

        employee_dict = {}
        provisions = []

        for t in TextUnit.objects.filter(document_id=document_id, unit_type="paragraph").all():
            paragraph_text = t.text
            # skip if all text in uppercase
            if paragraph_text == paragraph_text.upper():
                continue
            try:
                sentences = segment_sentences(paragraph_text)
            except:
                # accept the paragraph is a sentence if segmenter errors out.
                sentences = [paragraph_text]
            for text in sentences:

                # clean
                text = text.replace('[', '(').replace(']', ')')

                # get values not yet found. This logic assumes only one of each
                # of these values found per document.
                # if there is more than one it will only pick up the first (except effective date)
                if employee_dict.get('name') is None:
                    employee_dict['name'] = get_employee_name(text)
                if employee_dict.get('employer') is None:
                    employee_dict['employer'] = get_employer_name(text)
                if employee_dict.get('annual_salary') is None:
                    get_salary_result = get_salary(text)
                    if get_salary_result is not None:
                        employee_dict['annual_salary'] = get_salary_result[0][0] * \
                                                         get_salary_result[1]
                        employee_dict['salary_currency'] = get_salary_result[0][1]
                if employee_dict.get('effective_date') is None:
                    employee_dict['effective_date'] = get_effective_date(text)
                if employee_dict.get('vacation') is None:
                    get_vacation_result = get_vacation_duration(text)
                    if get_vacation_result is not None:
                        yearly_amount = get_vacation_result[0][1] * get_vacation_result[1]
                        employee_dict['vacation'] = str(yearly_amount) + " " + str(
                            get_vacation_result[0][0]) + "s"
                if employee_dict.get('governing_geo') is None:
                    employee_dict['governing_geo'] = get_governing_geo(text)

            non_compete_similarity = get_similar_to_non_compete(text)
            if non_compete_similarity > .5:
                provisions.append({"text_unit": t.id,
                                   "similarity": non_compete_similarity,
                                   "type": "noncompete"})

                termination_similarity = get_similar_to_termination(text)
                if termination_similarity > .5:
                    provisions.append({"text_unit": t.id,
                                       "similarity": termination_similarity,
                                       "type": "termination"})

                benefits_similarity = get_similar_to_benefits(text)
                if benefits_similarity > .5:
                    provisions.append({"text_unit": t.id,
                                       "similarity": benefits_similarity,
                                       "type": "benefits"})
                severance_similarity = get_similar_to_severance(text)
                if severance_similarity > .5:
                    provisions.append({"text_unit": t.id,
                                       "similarity": severance_similarity,
                                       "type": "severance"})

        employee = employer = None
        # create Employee only if his/her name exists
        if employee_dict.get('name') is not None:
            employee, ee_created = Employee.objects.get_or_create(
                name=employee_dict['name'],
                annual_salary=employee_dict.get('annual_salary'),
                salary_currency=employee_dict.get('salary_currency'),
                effective_date=employee_dict.get('effective_date'),
                vacation_yearly=employee_dict.get('vacation'),
                governing_geo=employee_dict.get('governing_geo'),
                document=Document.objects.get(pk=document_id)
            )

        if len(provisions) > 0 and employee is not None:
            noncompete_found = termination_found = \
                severance_found = benefits_found = False

            for i in provisions:
                if i["type"] == "noncompete":
                    noncompete_found = True
                else:
                    if i["type"] == "termination":
                        termination_found = True
                    else:
                        if i["type"] == "benefits":
                            benefits_found = True
                        else:
                            if i["type"] == "severance":
                                severance_found = True
                Provision.objects.get_or_create(
                    text_unit=TextUnit.objects.get(pk=i["text_unit"]),
                    similarity=i["similarity"],
                    employee=employee,
                    document=Document.objects.get(pk=document_id),
                    type=i["type"]
                )
            employee.has_noncompete = noncompete_found
            employee.has_termination = termination_found
            employee.has_benefits = benefits_found
            employee.has_severance = severance_found
            employee.save()

        # create Employer
        if employee and employee_dict.get('employer') is not None:
            employer, er_created = Employer.objects.get_or_create(name=employee_dict['employer'])

        if employee and employer and not employee.employer:
            employee.employer = employer
            employee.save()


app.register_task(LocateEmployees())
