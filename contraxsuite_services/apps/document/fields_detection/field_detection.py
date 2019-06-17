from typing import Optional, List, Dict, Any, Set, Iterable

from django.db.models import Prefetch

from apps.common.log_utils import ProcessLogger, ErrorCollectingLogger
from apps.common.log_utils import render_error
from apps.document.field_types import FieldType
from apps.document.fields_processing import field_value_cache
from apps.document.fields_processing.field_processing_utils import merge_detected_field_values_to_python_value, \
    order_field_detection
from apps.document.models import ClassifierModel, DocumentFieldValue
from apps.document.models import Document, DocumentType, DocumentField
from apps.users.models import User
from .field_based_ml_field_detection import FieldBasedMLOnlyFieldDetectionStrategy, \
    FieldBasedMLWithUnsureCatFieldDetectionStrategy
from .fields_detection_abstractions import DisabledFieldDetectionStrategy, \
    DetectedFieldValue, FieldDetectionStrategy
from .formula_and_field_based_ml_field_detection import FormulaAndFieldBasedMLFieldDetectionStrategy
from .formula_based_field_detection import FormulaBasedFieldDetectionStrategy
from .python_coded_field_detection import PythonCodedFieldDetectionStrategy
from .regexps_and_text_based_ml_field_detection import \
    RegexpsAndTextBasedMLFieldDetectionStrategy, TextBasedMLFieldDetectionStrategy
from .regexps_field_detection import RegexpsOnlyFieldDetectionStrategy, \
    FieldBasedRegexpsDetectionStrategy

STRATEGY_DISABLED = DisabledFieldDetectionStrategy()

_FIELD_DETECTION_STRATEGIES = [FieldBasedMLOnlyFieldDetectionStrategy(),
                               FieldBasedMLWithUnsureCatFieldDetectionStrategy(),
                               FormulaAndFieldBasedMLFieldDetectionStrategy(),
                               FormulaBasedFieldDetectionStrategy(),
                               RegexpsOnlyFieldDetectionStrategy(),
                               RegexpsAndTextBasedMLFieldDetectionStrategy(),
                               TextBasedMLFieldDetectionStrategy(),
                               PythonCodedFieldDetectionStrategy(),
                               FieldBasedRegexpsDetectionStrategy(),
                               STRATEGY_DISABLED]

FIELD_DETECTION_STRATEGY_REGISTRY = {st.code: st for st in _FIELD_DETECTION_STRATEGIES}


def train_document_field_detector_model(log: ProcessLogger,
                                        field: DocumentField,
                                        train_data_project_ids: Optional[List],
                                        use_only_confirmed_field_values: bool = False,
                                        train_documents: Iterable[Document] = None) -> Optional[ClassifierModel]:
    strategy = FIELD_DETECTION_STRATEGY_REGISTRY[
        field.value_detection_strategy] \
        if field.value_detection_strategy else STRATEGY_DISABLED

    return strategy.train_document_field_detector_model(log,
                                                        field,
                                                        train_data_project_ids,
                                                        use_only_confirmed_field_values,
                                                        train_documents)


def detect_and_cache_field_values(log: ProcessLogger,
                                  doc: Document,
                                  field: DocumentField,
                                  save: bool = True) -> Optional[List[DetectedFieldValue]]:
    strategy = FIELD_DETECTION_STRATEGY_REGISTRY[
        field.value_detection_strategy] \
        if field.value_detection_strategy else STRATEGY_DISABLED

    doc_field_values = None
    if strategy.uses_cached_document_field_values(field):
        doc_field_values = field_value_cache.cache_field_values(doc, None, save=False)
    detected_values = strategy.detect_field_values(log, doc, field, doc_field_values)
    if save:
        field_value_cache.cache_field_values(doc, detected_values,
                                             save=True,
                                             log=log)
        save_detected_values(doc, field, detected_values)
    return detected_values


def save_detected_values(document: Document,
                         field: DocumentField,
                         detected_values: List[DetectedFieldValue]):
    if len(detected_values) == 0:
        return 0

    field_type_adapter = field.get_field_type() # type: FieldType

    if field.is_choice_field() and not field_type_adapter.multi_value:
        values_order = field.get_choice_values()
        for choice_value in values_order:
            for dv in detected_values:
                if choice_value == dv.value:
                    field_type_adapter.save_value(document,
                                                  field,
                                                  dv.get_annotation_start(),
                                                  dv.get_annotation_end(),
                                                  dv.get_annotation_text(),
                                                  dv.text_unit,
                                                  dv.value,
                                                  user=dv.user,
                                                  allow_overwriting_user_data=dv.user is not None,
                                                  extraction_hint=dv.hint_name)
                    return 1
    else:
        for dv in detected_values:
            field_type_adapter.save_value(document,
                                          field,
                                          dv.get_annotation_start(),
                                          dv.get_annotation_end(),
                                          dv.get_annotation_text(),
                                          dv.text_unit,
                                          dv.value,
                                          user=dv.user,
                                          allow_overwriting_user_data=dv.user is not None,
                                          extraction_hint=dv.hint_name)
        return len(detected_values)


def detect_and_cache_field_values_for_document(log: ProcessLogger,
                                               document: Document,
                                               save: bool = True,
                                               clear_old_values: bool = True,
                                               changed_by_user: User = None,
                                               system_fields_changed: bool = False,
                                               generic_fields_changed: bool = False,
                                               document_initial_load: bool = False,
                                               ignore_field_codes: Set[str] = None):
    """
    Detects field values for a document and stores their DocumentFieldValue objects as well as Document.field_value.
    These two should always be consistent.
    :param log:
    :param document:
    :param save:
    :param clear_old_values:
    :param changed_by_user
    :param system_fields_changed
    :param generic_fields_changed
    :param document_initial_load
    :return:
    """

    save_cache = save
    save_detected = save
    if save and document.status and not document.status.is_active:
        log.info('Forbidden storing detected field values for document with "completed"'
                 ' status, document #{} ({})'.format(document.id, document.name))
        save_detected = False

    document_type = document.document_type  # type: DocumentType

    all_fields = document_type.fields \
        .all() \
        .prefetch_related(Prefetch('depends_on_fields', queryset=DocumentField.objects.only('uid').all()))

    all_fields = list(all_fields)

    fields_and_deps = [(f.code, f.get_depends_on_codes() or set()) for f in all_fields]
    sorted_codes = order_field_detection(fields_and_deps)
    all_fields_code_to_field = {f.code: f for f in all_fields}  # type: Dict[str, DocumentField]

    field_values_pre_cached = False

    res = list()
    for field_code in sorted_codes:
        if ignore_field_codes and field_code in ignore_field_codes:
            continue

        field = all_fields_code_to_field[field_code]  # type: DocumentField
        field_detection_strategy = FIELD_DETECTION_STRATEGY_REGISTRY[
            field.value_detection_strategy]  # type: FieldDetectionStrategy

        try:
            field_vals = field_value_cache.cache_field_values(document, None, save=False)
            detected_values = field_detection_strategy.detect_field_values(log,
                                                                           document,
                                                                           field,
                                                                           field_vals)  # type: List[DetectedFieldValue]
        except Exception as e:
            msg = '''Unable to detect field value. 
            Document type: {0} 
            Document: {1} 
            Field: {2}'''.format(document_type.code, document.pk, field.code)
            log.error(render_error(msg, e))
            raise e

        if save_detected and clear_old_values:
            # Delete previously detected values
            # to avoid accumulating garbage on each iteration.
            DocumentFieldValue.objects \
                .filter(document=document,
                        field=field,
                        removed_by_user=False,
                        created_by__isnull=True,
                        modified_by__isnull=True) \
                .exclude(field__value_detection_strategy=DocumentField.VD_DISABLED) \
                .delete()

        if detected_values:
            res.extend(detected_values)
            if save_detected:
                save_detected_values(document, field, detected_values)

    if save_cache:
        field_value_cache.cache_field_values(document, suggested_field_values=res,
                                             save=True, log=log,
                                             changed_by_user=changed_by_user,
                                             system_fields_changed=system_fields_changed,
                                             generic_fields_changed=generic_fields_changed,
                                             document_initial_load=document_initial_load)

    return res


def suggest_field_value(field: DocumentField, document: Document, log: ProcessLogger = None):
    if not log:
        log = ErrorCollectingLogger()
    detected_field_values = detect_and_cache_field_values(log, document, field,
                                                          save=False)  # type: List[DetectedFieldValue]

    field_codes_to_values = merge_detected_field_values_to_python_value(detected_field_values)  # type: Dict[str, Any]

    return field_codes_to_values.get(field.code)
