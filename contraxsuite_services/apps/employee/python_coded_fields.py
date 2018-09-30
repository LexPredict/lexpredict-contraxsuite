from apps.document.python_coded_fields import PythonCodedField
from apps.employee.services import get_employee_name, get_employer_name, get_salary
from typing import List, Any, Tuple
from apps.document.field_types import PersonField, AmountField


class EmployeeName(PythonCodedField):
    code = 'employment.employee_name'
    title = 'Employment: Employee Name'
    type = PersonField.code
    by_sentence = True

    def get_values(self, text: str) -> List[Tuple[Any, int, int]]:
        res = get_employee_name(text)
        return [(res, 0, len(text))] if res else None


class EmployerName(PythonCodedField):
    code = 'employment.employer_name'
    title = 'Employment: Employer Name'
    type = PersonField.code
    by_sentence = True

    def get_values(self, text: str) -> List[Tuple[Any, int, int]]:
        res = get_employer_name(text)
        return [(res, 0, len(text))] if res else None


class Salary(PythonCodedField):
    code = 'employment.salary'
    title = 'Employment: Salary'
    type = AmountField.code
    by_sentence = True

    def get_values(self, text: str) -> List[Tuple[Any, int, int]]:
        res = get_salary(text)
        if not res:
            return None
        money, _found_time_unit = res
        return [(money, 0, len(text))] if money else None


# Python coded fields enlisted in this attribute will be automatically registered on Django start.
# See apps.document.python_coded_fields.init_field_registry().
PYTHON_CODED_FIELDS = [EmployeeName(), EmployerName(), Salary()]
