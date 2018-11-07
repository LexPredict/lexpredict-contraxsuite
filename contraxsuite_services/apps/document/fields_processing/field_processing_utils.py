from typing import List, Dict, Any, Tuple, Set, Union

from apps.document.field_types import FieldType
from apps.document.fields_detection.fields_detection_abstractions import DetectedFieldValue
from apps.document.models import DocumentFieldValue


def order_field_detection(fields_and_deps: List[Tuple[str, Set[str]]]) -> List:
    """
    Sorts fields in their dependency resolving order (topology search).
    Based on https://stackoverflow.com/questions/11557241/python-sorting-a-dependency-list
    :param fields_and_deps:
    :return:
    """
    res = []
    pending = list(fields_and_deps)
    emitted = []
    while pending:
        next_pending = []
        next_emitted = []
        for entry in pending:
            uid, deps = entry
            deps.difference_update(emitted)  # remove deps we emitted last pass
            if deps:  # still has deps? recheck during next pass
                next_pending.append(entry)
            else:  # no more deps? time to emit
                res.append(uid)
                emitted.append(uid)  # <-- not required, but helps preserve original ordering
                next_emitted.append(uid)  # remember what we emitted for difference_update() in next pass
        if not next_emitted:  # all entries have unmet deps, one of two things is wrong...
            raise ValueError("Cyclic or missing dependency detected: %r" % (next_pending,))
        pending = next_pending
        emitted = next_emitted
    return res


def merge_detected_field_values_to_python_value(detected_field_values: List[Union[DetectedFieldValue,
                                                                                  DocumentFieldValue]]) \
        -> Dict[str, Any]:
    field_codes_to_merged_python_values = dict()

    for fv in detected_field_values:  # type: Union[DetectedFieldValue, DocumentFieldValue]
        field = fv.field
        field_type = fv.field.get_field_type()  # type: FieldType
        field_codes_to_merged_python_values[field.code] = field_type \
            .merge_multi_python_values(field_codes_to_merged_python_values.get(field.code), fv.python_value)

    return field_codes_to_merged_python_values


def merge_document_field_values_to_python_value(detected_field_values: List[Union[DetectedFieldValue,
                                                                                  DocumentFieldValue]]) \
        -> Dict[str, Any]:
    return merge_detected_field_values_to_python_value(detected_field_values)
