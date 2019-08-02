from tests.django_test_case import *
from django.test import TestCase
from apps.common.model_utils.model_class_dictionary import ModelClassDictionary


class TestModelClassDictionary(TestCase):
    def test_mcd_get_model(self):
        mdc = ModelClassDictionary()
        doc_class = mdc.model_by_table['document_document']
        self.assertIsNotNone(doc_class)
        self.assertEqual('Document', doc_class.__name__)

        model_name = mdc.get_model_class_name('document_document')
        self.assertEqual('Document', model_name)

        model_name = mdc.get_model_class_name_hr('document_documentfieldvalue')
        self.assertEqual('Document Field Value', model_name)
