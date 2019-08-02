from tests.django_test_case import *
from apps.common.model_utils.table_deps_builder import TableDepsBuilder
from apps.common.model_utils.table_deps import TableDeps, DependencyRecord
from django.test import TestCase


class TestBuildDocumentRelations(TestCase):
    def test_parse_deps(self):
        text = ''
        deps = TableDeps.parse_stored_deps_multiline(text)
        self.assertEqual(0, len(deps))

        text = \
        """
        pk:[id], document_documentnote.field_value_id -> document_documentfieldvalue.id, document_documentfieldvalue.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id

        pk:[id], extract_trademarkusage.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        """
        deps = TableDeps.parse_stored_deps_multiline(text)
        self.assertEqual(2, len(deps))
        self.assertEqual(3, len(deps[0].deps))
        self.assertEqual('extract_trademarkusage', deps[1].deps[0].own_table)
        self.assertEqual('text_unit_id', deps[1].deps[0].ref_key)
        self.assertEqual('document_document', deps[0].deps[-1].ref_table)
        self.assertEqual('id', deps[0].deps[-1].ref_table_pk)

    def test_build_document_relations(self):
        all_deps = TableDepsBuilder.build_table_dependences('document_document')
        all_deps_str = '\n'.join([str(d) for d in all_deps])
        print(all_deps_str)
        self.assertGreater(len(all_deps), 10)

