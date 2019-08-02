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
# -*- coding: utf-8 -*-

from typing import List, Any, Tuple, Optional

from apps.document.field_types import PersonField, AmountField
from apps.document.python_coded_fields import PythonCodedField
from apps.document.models import Document, DocumentField
from apps.employee.services import get_employee_name, get_employer_name, get_salary

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class EmployeeName(PythonCodedField):
    code = 'employment.employee_name'
    title = 'Employment: Employee Name'
    type = PersonField.code
    detect_per_text_unit = True

    def get_values(self, field: DocumentField, doc: Document, text: str) \
            -> List[Tuple[Any, Optional[int], Optional[int]]]:
        res = get_employee_name(text)
        return [(res, 0, len(text))] if res else None


class EmployerName(PythonCodedField):
    code = 'employment.employer_name'
    title = 'Employment: Employer Name'
    type = PersonField.code
    detect_per_text_unit = True

    def get_values(self, field: DocumentField, doc: Document, text: str) \
            -> List[Tuple[Any, Optional[int], Optional[int]]]:
        res = get_employer_name(text)
        return [(res, 0, len(text))] if res else None


class Salary(PythonCodedField):
    code = 'employment.salary'
    title = 'Employment: Salary'
    type = AmountField.code
    detect_per_text_unit = True

    def get_values(self, field: DocumentField, doc: Document, text: str) \
            -> List[Tuple[Any, Optional[int], Optional[int]]]:
        res = get_salary(text)
        if not res:
            return []
        money, _found_time_unit = res
        return [(money, 0, len(text))] if money else None


# Python coded fields enlisted in this attribute will be automatically registered on Django start.
# See apps.document.python_coded_fields.init_field_registry().
PYTHON_CODED_FIELDS = [EmployeeName(), EmployerName(), Salary()]
