import os

import django
from django.test import TestCase


def init_django():
    os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
    try:
        django.setup()
    except:
        pass


class DjangoTestCase(TestCase):
    def __init__(self, methodName='runTest'):
        init_django()
        super().__init__(methodName)


init_django()
