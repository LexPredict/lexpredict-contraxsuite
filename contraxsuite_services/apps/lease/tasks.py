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

from datetime import timedelta
from typing import List, Tuple

import geocoder
from celery import shared_task
from lexnlp.nlp.en.segments.sentences import get_sentence_list

from apps.celery import app
from apps.document.models import Document
from apps.extract.models import Party
from apps.lease.models import LeaseDocument
from apps.lease.parsing.lease_doc_detector import LeaseDocDetector
from apps.lease.parsing.lease_doc_properties_locator import find_landlord_tenant, detect_fields, \
    detect_address_default
from apps.task.tasks import BaseTask, ExtendedTask

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.1/LICENSE"
__version__ = "1.1.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

MODULE_NAME = __name__


class ProcessLeaseDocuments(BaseTask):
    name = 'Process Lease Documents'

    lease_doc_detector = LeaseDocDetector()

    def process(self, **kwargs):
        self.log_info(
            "Going to detect lease documents among the all loaded documents in the system...")

        if kwargs.get('delete'):
            for ld in LeaseDocument.objects.all():
                ld.delete(keep_parents=True)

        documents = Document.objects.all()
        # TODO: outdated
        if kwargs.get('document_type'):
            documents = documents.filter(document_type__in=kwargs['document_type'])
            self.log_info(
                'Filter documents by "%s" document type.' % str(kwargs['document_type']))

        if kwargs.get('document_id'):
            documents = documents.filter(pk=kwargs['document_id'])
            self.log_info('Process document id={}.'.format(kwargs['document_id']))

        detect_and_process_lease_document_args = []
        for row in documents.values_list('id'):
            detect_and_process_lease_document_args \
                .append((row[0], kwargs.get('no_detect', True)))
        self.run_sub_tasks('Detect And Process Each Lease Document',
                                ProcessLeaseDocuments.detect_and_process_lease_document,
                                detect_and_process_lease_document_args)

    @staticmethod
    @shared_task(base=ExtendedTask, bind=True)
    def detect_and_process_lease_document(task:ExtendedTask, document_id: int, no_detect: bool):
        doc = Document.objects.get(pk=document_id)
        doc_text = doc.full_text

        try:
            lease_doc = LeaseDocument.objects.get(pk=document_id)
        except:
            lease_doc = None

        if lease_doc or no_detect or ProcessLeaseDocuments.lease_doc_detector.is_lease_document(
                doc_text):
            task.log_info('{2} lease document: #{0}. {1}'
                               .format(document_id,
                                       doc.name,
                                       'Processing' if no_detect else 'Detected'))
            if not lease_doc:
                lease_doc = LeaseDocument(document_ptr=doc)
                lease_doc.__dict__.update(doc.__dict__)

            ProcessLeaseDocuments.process_landlord_tenant(lease_doc, doc_text)
            ProcessLeaseDocuments.process_fields(lease_doc, doc_text, task)

            lease_doc.save()

        else:
            task.log_info('Not a lease document: #{0}. {1}'.format(document_id, doc.name))

    @staticmethod
    def get_or_create_party(company_desc: Tuple) -> Party:
        name, _type, type_abbr, type_label, type_desc = company_desc
        defaults = dict(
            type=_type.upper() if _type else None,
            type_label=type_label.upper() if type_label else None,
            type_description=type_desc.upper() if type_desc else None
        )
        party, _ = Party.objects.get_or_create(
            name=name.upper() if name else None,
            type_abbr=type_abbr.upper() if type_abbr else None,
            defaults=defaults
        )
        return party

    @staticmethod
    def process_landlord_tenant(doc: LeaseDocument, doc_text: str):
        landlord, tenant = find_landlord_tenant(doc_text)

        doc.lessor = landlord
        doc.lessee = tenant

    @staticmethod
    def ordered_list_without_repetitions(sentence_list: List[str], separator: str = '\n'):
        if not sentence_list:
            return None
        sentence_list_no_repeat = list()
        for sentence in sentence_list:
            if sentence not in sentence_list_no_repeat:
                sentence_list_no_repeat.append(sentence)
        return separator.join(sentence_list_no_repeat)

    @staticmethod
    def process_fields(doc: LeaseDocument, doc_text: str, task: ExtendedTask):
        sentences = get_sentence_list(doc_text)
        # fields = detect_fields(sentences, groups=('address',))
        fields = detect_fields(sentences)

        doc.address = fields.get('address')
        if not doc.address:
            doc.address = detect_address_default(doc_text, sentences)

        if doc.address:
            g = geocoder.google(doc.address)
            if g.ok:
                doc.address_latitude = g.lat
                doc.address_longitude = g.lng
                doc.address_country = g.country_long
                doc.address_state_province = g.province_long
            elif g.status and 'ZERO' in g.status:
                # Google does not know such address - probably we detected it wrong.
                doc.address = None
                doc.address_state_province = None
                doc.address_country = None
                doc.address_longitude = None
                doc.address_latitude = None
            else:
                task.log_warn(
                    'Google did not return geocode info for: {0}\nResponse: {1}'.format(doc.address,
                                                                                        g))
        # return

        # term
        doc.commencement_date = fields.get('commencement_date')
        doc.expiration_date = fields.get('expiration_date')

        term_tuple = fields.get('term')
        if term_tuple:
            term = timedelta(days=term_tuple[2])
            if doc.commencement_date and not doc.expiration_date:
                doc.expiration_date = doc.commencement_date + term
            elif not doc.commencement_date and doc.expiration_date:
                doc.commencement_date = doc.expiration_date - term

        if doc.commencement_date \
                and doc.expiration_date \
                and doc.commencement_date >= doc.expiration_date:
            doc.expiration_date = None

        # lease type
        pay_taxes = int(fields.get('pay_taxes') or False)
        pay_costs = int(fields.get('pay_costs') or False)
        pay_insurance = int(fields.get('pay_insurance') or False)
        lt = pay_taxes + pay_costs + pay_insurance
        if lt == 3:
            doc.lease_type = 'triple-net'
        elif lt == 2:
            doc.lease_type = 'double-net'
        elif lt == 1:
            doc.lease_type = 'single-net'
        else:
            doc.lease_type = 'gross'

        # property type
        property_types = list(fields.get('property_types__set') or set())
        property_types.sort()
        doc.property_type = '; '.join(property_types)

        # permitted use
        doc.permitted_uses = fields.get('permitted_use')

        # prohibited use
        doc.prohibited_uses = ProcessLeaseDocuments.ordered_list_without_repetitions(
            fields.get('prohibited_use__list'))
        renew_duration_tuple = fields.get('renew_non_renew_notice')
        if renew_duration_tuple:
            doc.renew_non_renew_notice_duration = timedelta(days=renew_duration_tuple[2])

        auto_renew = fields.get('auto_renew')
        if auto_renew is not None:
            doc.auto_renew = auto_renew

        area_square_feet_list = fields.get('area_square_feet__list')
        if area_square_feet_list:
            doc.area_size_sq_ft = area_square_feet_list[0]

        doc.alterations_allowed = ProcessLeaseDocuments.ordered_list_without_repetitions(
            fields.get('alterations_allowed__list'))

        security_deposit = fields.get('security_deposit__set')
        if security_deposit:
            doc.security_deposit = max(security_deposit)

        doc.rent_due_frequency = fields.get('rent_due_frequency')

        mean_rent_per_month = fields.get('mean_rent_per_month__set')
        if mean_rent_per_month:
            doc.mean_rent_per_month = max(mean_rent_per_month)


app.register_task(ProcessLeaseDocuments())
