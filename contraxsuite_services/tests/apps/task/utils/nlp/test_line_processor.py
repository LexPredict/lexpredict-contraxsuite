from tests.django_test_case import *
from apps.task.utils.nlp.line_processor import LineProcessor
from django.test import TestCase


class TestLineProcessor(TestCase):

    def test_line_processor_lines(self):
        text = """
    aaa
    Bb b
    c"""
        proc = LineProcessor()
        lines = [line for line in proc.split_text_on_line_with_endings(text)]
        assert len(lines) == 3

