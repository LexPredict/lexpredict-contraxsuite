from tests.django_test_case import *
from unittest import TestCase
from apps.document.fields_processing.field_processing_utils import \
    order_field_detection, get_dependent_fields


class TestFieldsProcessingUtils(TestCase):
    def test_order_field_detection(self) -> None:
        fields = [('a', set()), ('b', set('a')), ('c', set('d')), ('d', set('b')), ('e', set())]
        ordered = order_field_detection(fields)
        ordered_pos = {ordered[i]:i for i in range(len(ordered))}
        self.assertEqual(len(fields), len(ordered))
        self.assertGreater(ordered_pos['b'], ordered_pos['a'])
        self.assertGreater(ordered_pos['c'], ordered_pos['d'])
        self.assertGreater(ordered_pos['d'], ordered_pos['b'])

    def test_required_fields(self) -> None:
        fields = [('a', set()), ('b', set('a')), ('c', set('d')), ('d', set('b')), ('e', set())]
        deps = get_dependent_fields(fields, {'b'})
        self.assertEqual(2, len(deps))
        self.assertIn('d', deps)
        self.assertIn('c', deps)

        deps = get_dependent_fields(fields, {'a'})
        self.assertEqual(3, len(deps))
        self.assertTrue('a' not in deps)

        deps = get_dependent_fields(fields, {'c'})
        self.assertEqual(0, len(deps))

    def test_order_field_detection_empty(self) -> None:
        ordered = order_field_detection([])
        self.assertEqual(0, len(ordered))
