# Standard imports
from collections import Iterable
from typing import Dict, Any, List, Optional

# Django imports
from django.contrib.postgres.aggregates.general import StringAgg
from django.db.models import Min, Max

from apps.common.log_utils import ProcessLogger
from apps.document.events import events
# Project imports
from apps.document.field_types import FIELD_TYPES_REGISTRY, FieldType
from apps.document.fields_detection.fields_detection_abstractions import DetectedFieldValue
from apps.document.fields_processing.field_processing_utils import merge_detected_field_values_to_python_value
from apps.document.models import DocumentField, Document, DocumentType
from apps.extract.models import CurrencyUsage

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.9/LICENSE"
__version__ = "1.1.9"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def cache_field_values(doc: Document,
                       suggested_field_values: Optional[List[DetectedFieldValue]],
                       save: bool = True,
                       log: ProcessLogger = None) -> Dict[str, Any]:
    """
    Loads DocumentFieldValue objects from DB, merges them to get python field values of their fields for the document,
    converts them to the sortable DB-aware form and saves them to Document.field_values.
    :param doc:
    :param save:
    :param suggested_field_values:
    :param log
    :return:
    """
    document_type = doc.document_type  # type: DocumentType
    # TODO: get/save field value for specific field
    all_fields = list(document_type.fields.all())

    related_info_field_uids = {f.uid for f in all_fields if f.is_related_info_field()}

    fields_to_field_values = {f: None for f in all_fields}

    for fv in doc.documentfieldvalue_set.all():
        if fv.removed_by_user:
            continue

        field = fv.field
        field_type = FIELD_TYPES_REGISTRY[fv.field.type]  # type: FieldType
        fields_to_field_values[field] = field_type \
            .merge_multi_python_values(fields_to_field_values.get(field), fv.python_value)

    field_uids_to_field_values_db = {}

    for f in all_fields:  # type: DocumentField
        field_type = FIELD_TYPES_REGISTRY[f.type]  # type: FieldType
        v = fields_to_field_values[f]
        field_uids_to_field_values_db[f.uid] = field_type.merged_python_value_to_db(v)

    if suggested_field_values:
        field_codes_to_suggested_values = \
            merge_detected_field_values_to_python_value(suggested_field_values)  # type: Dict[str, Any]
    else:
        field_codes_to_suggested_values = None

    for f in all_fields:  # type: DocumentField
        field_type = f.get_field_type()  # type: FieldType
        if f.is_detectable():
            suggested_field_uid = Document.get_suggested_field_uid(f.uid)
            if field_codes_to_suggested_values:
                suggested_value_db = field_type.merged_python_value_to_db(field_codes_to_suggested_values.get(f.code))
            else:
                suggested_value_db = doc.field_values.get(suggested_field_uid) if doc.field_values else None

            # suggested_value_db can be list, None or int, Iterable validation should be here
            if isinstance(suggested_value_db, Iterable) and f.is_related_info_field():
                suggested_value_db = len(suggested_value_db)
            field_uids_to_field_values_db[suggested_field_uid] = suggested_value_db

    if save:
        doc.field_values = {uid: len(value) if uid in related_info_field_uids and value is not None else value
                            for uid, value in field_uids_to_field_values_db.items()}
        doc.save()
        events.on_document_change(
            events.DocumentChangedEvent(log=log,
                                        document=doc,
                                        system_fields_changed=False,
                                        generic_fields_changed=False,
                                        user_fields_changed=True,
                                        pre_detected_field_values=field_codes_to_suggested_values))

    return field_uids_to_field_values_db


def get_generic_values(doc: Document) -> Dict[str, Any]:
    # If changing keys of the returned dictionary - please change field code constants
    # in apps/rawdb/field_value_tables.py accordingly (_FIELD_CODE_CLUSTER_ID and others)

    document_qs = Document.objects.filter(pk=doc.pk) \
        .annotate(cluster_id=Max('documentcluster'),
                  parties=StringAgg('textunit__partyusage__party__name',
                                    delimiter=', ',
                                    distinct=True),
                  min_date=Min('textunit__dateusage__date'),
                  max_date=Max('textunit__dateusage__date'))
    values = document_qs.values('cluster_id', 'parties', 'min_date',
                                'max_date').first()  # type: Dict[str, Any]

    max_currency = CurrencyUsage.objects.filter(text_unit__document_id=doc.id) \
        .order_by('-amount').values('currency', 'amount').first()  # type: Dict[str, Any]
    values['max_currency'] = max_currency
    values['max_currency_name'] = max_currency['currency'] if max_currency else None
    values['max_currency_amount'] = max_currency['amount'] if max_currency else None

    return values


def cache_generic_values(doc: Document, save: bool = True,
                         log: ProcessLogger = None):
    doc.generic_data = get_generic_values(doc)

    if save:
        doc.save(update_fields=['generic_data'])
        events.on_document_change(events.DocumentChangedEvent(log=log,
                                                              document=doc,
                                                              system_fields_changed=False,
                                                              generic_fields_changed=True,
                                                              user_fields_changed=False,
                                                              pre_detected_field_values=None))
