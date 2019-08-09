"""
    Copyright (C) 2017, ContraxSuite, LLC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    You can also be released from the requirements of the license by purchasing
    a commercial license from ContraxSuite, LLC. Buying such a license is
    mandatory as soon as you develop commercial activities involving ContraxSuite
    software without disclosing the source code of your own applications.  These
    activities include: offering paid services to customers as an ASP or "cloud"
    provider, processing documents on the fly in a web application,
    or shipping ContraxSuite within a closed source product.
"""
# -*- coding: utf-8 -*-

from typing import List, Dict, Any, Tuple, Set, Union

from apps.document.field_types import FieldType
from apps.document.fields_detection.fields_detection_abstractions import DetectedFieldValue
from apps.document.models import DocumentFieldValue, DocumentField

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def order_field_detection(
        fields_and_deps: List[Tuple[str, Set[str]]]) -> List:
    """
    Sorts fields in their dependency resolving order (topology search).
    Based on https://stackoverflow.com/questions/11557241/python-sorting-a-dependency-list
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
            er_msg = "Cyclic or missing dependency detected: %r\nFields are:" % (next_pending,)
            all_fields = ', '.join(['"{}"{}'.format(f[0], ': [' + str(f[1]) + ']'
                if len(f[1]) > 0 else '') for f in fields_and_deps])
            er_msg += all_fields
            raise ValueError(er_msg)
        pending = next_pending
        emitted = next_emitted
    return res


def get_dependent_fields(
        fields_and_deps: List[Tuple[str, Set[str]]],
        required_fields: Set[str] = None) -> Set[str]:
    """
    get the field that is passed and all the fields
    recursively dependent from the passed one
    """
    required = set(required_fields)
    dependent = set()  # type: Set[str]

    while True:
        found_new = False
        for fd in fields_and_deps:
            if fd[0] in required:
                continue
            for deps in fd[1]:
                if deps not in required:
                    continue
                required.add(fd[0])
                dependent.add(fd[0])
                found_new = True
        if not found_new:
            break
    return dependent


def merge_detected_field_values_to_python_value(detected_field_values: List[Union[DetectedFieldValue,
                                                                                  DocumentFieldValue]],
                                                return_extended=False) \
        -> Dict[str, Any]:
    field_codes_to_merged_python_values = dict()
    codes_to_fields = dict()  # type: Dict[str, DocumentField]

    for fv in detected_field_values:  # type: Union[DetectedFieldValue, DocumentFieldValue]
        field = fv.field
        field_type = fv.field.get_field_type()  # type: FieldType
        codes_to_fields[field.code] = field
        field_codes_to_merged_python_values[field.code] = field_type \
            .merge_multi_python_values(field_codes_to_merged_python_values.get(field.code), fv.python_value)
    if not return_extended:
        return field_codes_to_merged_python_values
    else:
        res = dict()
        for code, value in field_codes_to_merged_python_values.items():
            res[code] = {
                'code': code,
                'type': codes_to_fields[code].type,
                'title': codes_to_fields[code].title,
                'order': codes_to_fields[code].order,
                'value': value
            }
        return res


def build_field_value_by_id_hash(detected_field_values: List[Union[DetectedFieldValue,
                                                                         DocumentFieldValue]]) \
        -> Dict[str, Any]:
    field_codes_to_merged_python_values = dict()

    for fv in detected_field_values:  # type: Union[DetectedFieldValue, DocumentFieldValue]
        field = fv.field
        field_type = fv.field.get_field_type()  # type: FieldType
        field_codes_to_merged_python_values[field.uid] = field_type \
            .merge_lists_of_python_values(field_codes_to_merged_python_values.get(field.uid), fv.python_value)
    return field_codes_to_merged_python_values


def merge_document_field_values_to_python_value(detected_field_values: List[Union[DetectedFieldValue,
                                                                                  DocumentFieldValue]],
                                                return_extended=False) \
        -> Dict[str, Any]:
    return merge_detected_field_values_to_python_value(detected_field_values,
                                                       return_extended=return_extended)
