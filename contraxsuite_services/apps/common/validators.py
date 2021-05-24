import re

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class RegexPatternValidator:
    message = _('Ensure this regular expression is correct.')

    def __init__(self, message=None):
        if message:
            self.message = message

    def __call__(self, value):
        if not self.check(value):
            raise ValidationError(self.message, params={'value': value})

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.message == other.message
        )

    def check(self, value):
        try:
            return bool(re.compile(value))
        except re.error:
            return False
