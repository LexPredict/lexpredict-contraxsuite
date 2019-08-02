from tests.django_test_case import *
from apps.common.model_utils.model_bulk_delete import ModelBulkDelete
from apps.common.model_utils.table_deps import TableDeps
from django.test import TestCase


class TestModelBulkDelete(TestCase):
    def test_build_select_queries(self):
        text = """
        pk:[id], document_documentnote.field_value_id -> document_documentfieldvalue.id, document_documentfieldvalue.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        """
        bd = self.build_bulk_delete(text)
        queries = bd.build_get_deleted_count_queries()
        self.assertEqual(1, len(queries))

        expected = """
        SELECT COUNT(*) FROM "document_documentnote"
            INNER JOIN "document_documentfieldvalue" ON "document_documentfieldvalue"."id" = "document_documentnote"."field_value_id"
            INNER JOIN "document_textunit" ON "document_textunit"."id" = "document_documentfieldvalue"."text_unit_id"
            INNER JOIN "document_document" ON "document_document"."id" = "document_textunit"."document_id"
        """.strip('\n ')
        expected = '\n'.join([l.strip(' ') for l in expected.split('\n')])

        resulted = queries[0]
        resulted = '\n'.join([l.strip(' ') for l in resulted.split('\n')])
        self.assertEqual(expected, resulted)

    def non_test_live_select_query(self):
        bd = self.build_bulk_delete()
        where_suffix = "\n  WHERE document_document.id IN (10, 12);"
        #where_suffix = ";"
        totals = bd.calculate_total_objects_to_delete(where_suffix)
        totals_str = '\n'.join([f'{t}: {totals[t]}' for t in totals])
        print(totals_str)

    def non_test_live_delete_query(self):
        bd = self.build_bulk_delete()
        where_suffix = "\n  WHERE document_document.id IN (10));"
        totals = bd.delete_objects(where_suffix)
        totals_str = '\n'.join([f'{t}: {totals[t]}' for t in totals])
        print(totals_str)

    def build_bulk_delete(self, dep_set_text:str='') -> ModelBulkDelete:
        full_depset = """
        pk:[id], document_documentnote.field_value_id -> document_documentfieldvalue.id, document_documentfieldvalue.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], extract_trademarkusage.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], extract_copyrightusage.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], extract_citationusage.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], extract_percentusage.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], extract_ratiousage.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], extract_distanceusage.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], employee_provision.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], document_documentfieldvalue.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], document_textunitnote.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], document_textunitproperty.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], document_textunitrelation.text_unit_b_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], analyze_textunitclassifiersuggestion.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], analyze_textunitcluster_text_units.textunit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], analyze_textunitsimilarity.text_unit_a_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], extract_partyusage.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], extract_geoentityusage.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], extract_dateusage.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], extract_currencyusage.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], document_textunittag.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], extract_urlusage.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], extract_amountusage.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], employee_employerusage.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], document_textunitrelation.text_unit_a_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], analyze_textunitclassification.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], analyze_textunitsimilarity.text_unit_b_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], extract_regulationusage.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], extract_termusage.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], extract_geoaliasusage.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], extract_definitionusage.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], extract_datedurationusage.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], extract_courtusage.text_unit_id -> document_textunit.id, document_textunit.document_id -> document_document.id
        pk:[id], fields_documentannotation_tags.documentannotation_id -> fields_documentannotation.id, fields_documentannotation.document_id -> document_document.id
        pk:[id], employee_provision.employee_id -> employee_employee.id, employee_employee.document_id -> document_document.id
        pk:[id], document_documentnote.field_value_id -> document_documentfieldvalue.id, document_documentfieldvalue.document_id -> document_document.id
        pk:[document_id], doc_fields_document_generic_document.document_id -> document_document.id
        pk:[id], employee_provision.document_id -> document_document.id
        pk:[id], project_taskqueue_completed_documents.document_id -> document_document.id
        pk:[id], document_documentrelation.document_b_id -> document_document.id
        pk:[id], document_textunit.document_id -> document_document.id
        pk:[id], analyze_documentsimilarity.document_b_id -> document_document.id
        pk:[document_ptr_id], lease_leasedocument.document_ptr_id -> document_document.id
        pk:[document_id], doc_fields_com_cred.document_id -> document_document.id
        pk:[id], imanage_integration_imanagedocument.document_id -> document_document.id
        pk:[id], fields_classifierdatasetentry.document_id -> document_document.id
        pk:[id], fields_documentannotation.document_id -> document_document.id
        pk:[id], employee_employee.document_id -> document_document.id
        pk:[id], document_documentfieldvalue.document_id -> document_document.id
        pk:[id], project_taskqueue_documents.document_id -> document_document.id
        pk:[id], document_documentnote.document_id -> document_document.id
        pk:[id], document_documentproperty.document_id -> document_document.id
        pk:[id], document_documentrelation.document_a_id -> document_document.id
        pk:[id], document_documenttag.document_id -> document_document.id
        pk:[id], project_taskqueuehistory_documents.document_id -> document_document.id
        pk:[id], analyze_documentcluster_documents.document_id -> document_document.id
        pk:[id], analyze_documentsimilarity.document_a_id -> document_document.id
        """
        dep_set_text = dep_set_text or full_depset
        deps = TableDeps.parse_stored_deps_multiline(dep_set_text)
        return ModelBulkDelete(deps)
