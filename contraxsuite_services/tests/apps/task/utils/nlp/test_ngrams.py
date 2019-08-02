from tests.django_test_case import *
from django.test import TestCase
from apps.task.utils.nlp.ngrams import get_word_ngram_distribution


class TestNgrams(TestCase):
    def test_get_word_ngram_distribution(self):
        text = "this is a foo bar sentences and i want to ngramize it"
        ngrs = get_word_ngram_distribution(text)
        self.assertEqual(12, len(ngrs))
