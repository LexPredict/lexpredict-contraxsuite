from tests.django_test_case import *
from decimal import Decimal
from unittest import TestCase
from apps.notifications.tasks import values_look_equal


class TestValuesLookEqual(TestCase):
    def test_values_look_equal_empty(self) -> None:
        self.assertTrue(values_look_equal(None, None))
        self.assertTrue(values_look_equal(None, ''))
        self.assertFalse(values_look_equal(None, 0))
        self.assertTrue(values_look_equal('', 0))

    def test_values_look_equal_numbers(self) -> None:
        self.assertTrue(values_look_equal(0, 0))
        self.assertTrue(values_look_equal(0.100000000001, 0.1))
        self.assertFalse(values_look_equal(0.1001, 0.1))
        self.assertTrue(values_look_equal(Decimal(0.100000000001), 0.1))
