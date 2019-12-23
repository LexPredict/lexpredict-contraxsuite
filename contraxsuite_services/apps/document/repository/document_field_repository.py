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

import datetime
import difflib
from collections import defaultdict
from typing import List, Dict, Any, Generator, Union, Iterable, Tuple
from typing import Set, Optional

from bulk_update.helper import bulk_update
from django.conf import settings
from django.db import connection, transaction
from django.db.models import QuerySet, Q, Subquery, F
from rest_framework.exceptions import APIException, NotFound

from apps.common.collection_utils import chunks
from apps.common.contraxsuite_urls import doc_editor_url
from apps.common.script_utils import eval_script
from apps.common.singleton import Singleton
from apps.common.sql_commons import sql_query
from apps.document.constants import ALL_DOCUMENT_FIELD_CODES
from apps.document.field_types import TypedField, MultiValueField
from apps.document.models import Document
from apps.document.models import DocumentType, DocumentField
from apps.document.models import FieldValue, FieldAnnotation, \
    FieldAnnotationFalseMatch
from apps.document.models import TextUnit
from apps.document.repository.dto import FieldValueDTO, AnnotationDTO
from apps.document.signals import fire_hidden_fields_cleared
from apps.rawdb.constants import FIELD_CODE_DOC_FULL_TEXT, \
    FIELD_CODE_DOC_ID, FIELD_CODE_HIDE_UNTIL_PYTHON
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.4.0/LICENSE"
__version__ = "1.4.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


YES = 'Yes'


class NoExistingAnnotationMatchingNewFieldValue(APIException):
    pass


class BadAnnotationValueForField(APIException):
    pass


class BadValueForField(APIException):
    pass


class ObjectNotFound(APIException):
    pass


class ChangingDocumentNotPermitted(APIException):
    pass


class ChangingFieldNotPermitted(APIException):
    pass


@Singleton
class DocumentFieldRepository:
    DEFAULT_FIELD_CODE_FILTER = {FIELD_CODE_DOC_ID, FIELD_CODE_DOC_FULL_TEXT}

    # =========================================================================
    # Readonly methods
    # =========================================================================

    def get_document_field_val_dtos(self,
                                    doc_id: int,
                                    field_codes_only: Optional[Set] = None) -> \
            Dict[str, FieldValueDTO]:  # field code: FieldValueDTO
        qr_field_values = FieldValue.objects.filter(document_id=doc_id)
        qr_ants = FieldAnnotation.objects.filter(document_id=doc_id)

        if field_codes_only:
            qr_field_values = qr_field_values.filter(field__code__in=field_codes_only)
            qr_ants = qr_ants.filter(field__code__in=field_codes_only)

        field_code_to_ants = defaultdict(list)  # type: Dict[str, List[AnnotationDTO]]

        for field_code, location_start, location_end, extraction_hint, value in qr_ants.values_list(
                'field__code',
                'location_start',
                'location_end',
                'extraction_hint',
                'value'):
            field_code_to_ants[field_code].append(AnnotationDTO(annotation_value=value,
                                                                location_in_doc_start=location_start,
                                                                location_in_doc_end=location_end,
                                                                extraction_hint_name=extraction_hint))

        field_code_to_fvals = dict()  # type: Dict[str, FieldValueDTO]
        for field_code, value in qr_field_values.values_list('field__code', 'value'):
            field_code_to_fvals[field_code] = FieldValueDTO(field_value=value,
                                                            annotations=field_code_to_ants.get(field_code))

        return field_code_to_fvals

    def get_document_own_and_field_values(
            self,
            document: Document,
            field_codes: Set[str] = None,
            need_field_values: bool = False):
        """
        Get fields either from document or from FieldValues stored for the document.
        We can request such fields as "formula" or "assignee_name".
        :param document: document with all its fields
        :param field_codes: fields to retrieve, None means all fields should be returned
        :param need_field_values: add FieldValue-s values in resulted hashset
        :return: {field_code: field_value}
        """
        field_by_code = None
        if not field_codes:
            field_codes = ALL_DOCUMENT_FIELD_CODES

        if need_field_values:
            field_by_code = self.get_document_field_code_by_id(document.document_type.pk)
            field_codes.update(field_by_code.values())

        doc_values = {}  # type: Dict[str, Any]
        field_codes_left = set(field_codes)

        for field_code in field_codes:
            fval, f_exists = document.try_get_field_by_code(field_code)
            if f_exists:
                field_codes_left.remove(field_code)
                doc_values[field_code] = fval

        # if there are fields left after trying to get values from Document object
        if not field_codes_left:
            return doc_values

        fvals = FieldValue.objects.filter(document_id=document.pk).values_list(
            'field_id', 'value')
        if not field_by_code:
            field_by_code = self.get_document_field_code_by_id(document.document_type.pk)
        for field_id, field_value in fvals:
            field_code = field_by_code[field_id]
            if field_code in field_codes_left:
                doc_values[field_code] = field_value
        return doc_values

    def get_document_field_code_by_id(self, doc_type_id: str):
        return {
            f[0]: f[1] for f in
            DocumentField.objects.filter(
                document_type_id=doc_type_id).values_list('pk', 'code')}

    def get_document_field_by_id(self, field_id: str) -> DocumentField:
        return DocumentField.objects.get(pk=field_id)

    def get_fieldant_ids_by_doc_field(self, document_field_id: int = None) -> Union[QuerySet, List[int]]:
        dfv_qs = FieldAnnotation.objects
        if document_field_id is not None:
            dfv_qs = dfv_qs.filter(field_id=document_field_id)
        else:
            dfv_qs = dfv_qs.all()
        return dfv_qs.values_list('pk', flat=True)

    def get_field_value_ids_by_doc_field(self, document_field_id: int = None) -> Union[QuerySet, List[int]]:
        dfv_qs = FieldValue.objects
        if document_field_id is not None:
            dfv_qs = dfv_qs.filter(field_id=document_field_id)
        else:
            dfv_qs = dfv_qs.all()
        return dfv_qs.values_list('pk', flat=True)

    def get_ants_by_ids(self, ids: Iterable[int]) -> Union[QuerySet, List[FieldAnnotation]]:
        qs = FieldAnnotation.objects \
            .filter(pk__in=ids) \
            .select_related('field')
        return qs

    def get_field_values_by_ids(self, ids: Iterable[int]) -> Union[QuerySet, List[FieldAnnotation]]:
        qs = FieldValue.objects \
            .filter(pk__in=ids) \
            .select_related('field')
        return qs

    def get_removed_fieldvals_doc_ids(self) -> List[int]:
        modified_document_ids = FieldAnnotationFalseMatch.objects \
            .distinct('document_id') \
            .values_list('document_id')
        return modified_document_ids

    def get_modified_field_ids(self,
                               documents: Union[QuerySet, List[Document]],
                               is_active: bool) -> QuerySet:
        return FieldValue.objects \
            .filter(document__in=Subquery(documents.values('pk').distinct('pk').order_by('pk')),
                    document__status__is_active=not is_active) \
            .values_list('field_id', flat=True) \
            .distinct('field_id').order_by('field_id')

    def get_annotated_values_for_dump(self) -> List[Dict]:
        data = FieldAnnotation.objects \
            .filter(modified_by__isnull=False,
                    text_unit__textunittext__text__isnull=False) \
            .annotate(text_unit_text=F('text_unit__textunittext__text')) \
            .values('field_id', 'value', 'extraction_hint',
                    'text_unit_text', 'modified_date')  # 'created_date'
        return data

    def get_filtered_field_values_count(self, field_id: int) -> int:
        user_values_number = FieldAnnotation.filter(field_id=field_id) \
                                 .filter(Q(modified_by__isnull=False)) \
                                 .count() + \
                             FieldAnnotationFalseMatch.filter(field_id=field_id) \
                                 .filter(Q(modified_by__isnull=False)) \
                                 .count()
        return user_values_number

    def get_doc_field_ids_with_values(self, doc_id: int) -> QuerySet:
        return FieldValue.objects \
            .filter(document_id=doc_id) \
            .values_list('field_id', flat=True) \
            .distinct()

    def get_field_code_to_python_value(self,
                                       doc_id: int,
                                       document_type_id: int = None,
                                       field_codes_only: Optional[Iterable[str]] = None) \
            -> Dict[str, Any]:

        if document_type_id is None:
            document_type_id = Document.objects.filter(pk=doc_id).values_list('document_type_id', flat=True).first()

        qr = FieldValue.objects.filter(document_id=doc_id)  # type: QuerySet
        fields = DocumentField.objects.filter(document_type_id=document_type_id)
        if field_codes_only and isinstance(field_codes_only, str):
            field_codes_only = {field_codes_only}
        if field_codes_only:
            qr = qr.filter(field__code__in=field_codes_only)
            fields = fields.filter(code__in=field_codes_only)

        field_code_to_field = {f.code: f for f in fields}  # type: Dict[str, DocumentField]

        res = dict()

        for field_code, value in qr.values_list('field__code', 'value'):
            field = field_code_to_field[field_code]
            typed_field = TypedField.by(field)
            res[field_code] = typed_field.field_value_json_to_python(value)

        return res

    def get_field_code_to_json_value(self,
                                     doc_id: int,
                                     field_codes_only: Optional[Iterable[str]] = None) \
            -> Dict[str, Any]:

        qr_values = FieldValue.objects.filter(document_id=doc_id)  # type: QuerySet

        if field_codes_only:
            qr_values = qr_values.filter(field__code__in=field_codes_only)

        return {field_code: value for field_code, value in qr_values.values_list('field__code', 'value')}

    def get_field_uid_to_python_value(self,
                                      doc_id: int,
                                      document_type_id: int = None,
                                      field_uids_only: Optional[Iterable[str]] = None) \
            -> Dict[str, Any]:
        if document_type_id is None:
            document_type_id = Document.objects.filter(pk=doc_id).values_list('document_type_id', flat=True).first()
        qr = FieldValue.objects.filter(document_id=doc_id)  # type: QuerySet
        fields = DocumentField.objects.filter(document_type_id=document_type_id)

        if field_uids_only:
            qr = qr.filter(field_id__in=field_uids_only)
            fields = fields.filter(pk__in=field_uids_only)

        field_uid_to_field = {f.pk: f for f in fields}  # type: Dict[str, DocumentField]

        res = dict()

        for field_uid, value in qr.values_list('field_id', 'value'):
            field = field_uid_to_field[field_uid]
            typed_field = TypedField.by(field)
            res[field_uid] = typed_field.field_value_json_to_python(value)

        return res

    def get_field_code_to_python_value_multiple_docs(self,
                                                     document_type_id: int,
                                                     doc_ids: Optional[Union[QuerySet, Iterable[int]]] = None,
                                                     project_ids: Optional[Union[QuerySet, Iterable[int]]] = None,
                                                     field_codes_only: Optional[Union[QuerySet, Iterable[str]]] = None,
                                                     doc_limit: int = None) \
            -> Generator[Tuple[int, Dict[str, Any]], None, None]:
        """
        Load field values for multiple documents. Generates tuples: (document_id, dict(field_code -> value)).
        :param document_type_id:
        :param doc_ids:
        :param project_ids:
        :param field_codes_only:
        :param doc_limit:
        :return: Generates tuples of (doc_id, dict of field_code -> python_value) for each document.
        """
        if doc_ids is None and project_ids is None:
            raise Exception('At least one filter must be specified: by doc ids, by project ids')

        qr = FieldValue.objects.all()  # type: QuerySet
        fields = DocumentField.objects.filter(document_type_id=document_type_id)

        if doc_ids is not None:
            qr = qr.filter(document_id__in=doc_ids)

        if project_ids is not None:
            qr = qr.filter(document__project_id__in=project_ids)

        if field_codes_only:
            qr = qr.filter(field__code__in=field_codes_only)
            fields = fields.filter(code__in=field_codes_only)

        field_code_to_field = {f.code: f for f in fields}  # type: Dict[str, DocumentField]

        qr = qr.order_by('document_id')

        doc_count = 0
        last_document_id = None
        last_field_values = None
        for document_id, field_code, value in qr.values_list('document_id', 'field__code', 'value'):
            if last_document_id != document_id:
                if last_document_id is not None:
                    yield last_document_id, last_field_values
                    doc_count += 1
                    if doc_limit and doc_count >= doc_limit:
                        return
                last_document_id = document_id
                last_field_values = dict()
            field = field_code_to_field[field_code]
            typed_field = TypedField.by(field)
            last_field_values[field_code] = typed_field.field_value_json_to_python(value)

        if last_field_values is not None:
            yield last_document_id, last_field_values

    def get_doc_field_values_filtered_count(self,
                                            field_id: int,
                                            filter_by_modified: bool = True) -> int:
        filters = (Q(field_id=field_id),)
        if filter_by_modified:
            filters = filters + (Q(modified_by__isnull=False),)
        # user_values_count = FieldValue.objects.filter(filters).count()
        user_values_count = FieldAnnotation.objects.filter(filters).count()
        return user_values_count

    def get_count_by_field(self, field_id: int) -> int:
        return self.get_doc_field_values_filtered_count(field_id,
                                                        filter_by_modified=False)

    def get_all_docfieldvalues(self):
        # return DocumentFieldValue.objects.all()
        # TODO: FieldValue or FieldAnnotation ?
        # DocumentNoteDetailSerializer probably requires FieldValue-s
        return FieldAnnotation.objects.all()

    def get_invalid_choice_vals_count(self,
                                      field: DocumentField) -> int:
        user_ants_qs = field.get_invalid_choice_annotations()  # type:Union[QuerySet, List[FieldAnnotation]]
        user_values_count = user_ants_qs.filter(
            modified_by__isnull=False).count()
        return user_values_count

    def field_value_exists(self,
                           doc_id: int,
                           field_id: str,
                           json_value: Any) -> bool:
        return FieldValue.objects.filter(document_id=doc_id,
                                         field_id=field_id,
                                         value=json_value).exists()

    def get_hidden_field_ids_codes(self, doc: Document, field_code_to_value: Dict[str, Any] = None) \
            -> Tuple[Set[int], Set[str]]:

        if not field_code_to_value:
            field_code_to_value = {code: None for code in doc.document_type.fields.all().values_list('code', flat=True)}
            field_code_to_value.update(self.get_field_code_to_python_value(document_type_id=doc.document_type_id,
                                                                           doc_id=doc.pk))

        hidden_field_ids = set()
        hidden_field_codes = set()

        for field_pk, field_code, formula in doc.document_type.fields \
                .filter(hide_until_python__isnull=False) \
                .values_list('pk', 'code', 'hide_until_python'):
            if not formula:
                continue
            eval_locals = dict()
            eval_locals.update(settings.CALCULATED_FIELDS_EVAL_LOCALS)
            eval_locals.update(field_code_to_value)
            displayed = eval_script(
                f'{field_code}.{FIELD_CODE_HIDE_UNTIL_PYTHON}', formula, eval_locals)
            if not displayed:
                hidden_field_ids.add(field_pk)
                hidden_field_codes.add(field_code)
        return hidden_field_ids, hidden_field_codes

    def get_docfield_ants_by_doc_and_code(self, document_id: int,
                                          field_codes: Set[str] = None,
                                          order_by_location: bool = False) -> \
            List[FieldAnnotation]:
        real_document_field_ants = FieldAnnotation.objects \
            .filter(document_id=document_id)  # type: QuerySet

        if field_codes:
            real_document_field_ants = FieldAnnotation.objects \
                .filter(document_id=document_id,
                        field__code__in=field_codes) \
                .select_related('field')
        if order_by_location:
            real_document_field_ants = real_document_field_ants.order_by('location_start')
        return list(real_document_field_ants)

    def delete_document_history_values(self, document_id: int):
        FieldValue.history.filter(document_id=document_id).delete()
        FieldAnnotation.history.filter(document_id=document_id).delete()
        FieldAnnotationFalseMatch.history.filter(document_id=document_id).delete()

    def delete_documents_history_values(self,
                                        doc_ids: Union[QuerySet, List[int]]):
        FieldValue.history.filter(document_id__in=doc_ids).delete()
        FieldAnnotation.history.filter(document_id__in=doc_ids).delete()
        FieldAnnotationFalseMatch.history.filter(document_id__in=doc_ids).delete()

    def lock_document(self, cursor, doc_id: int):
        cursor.execute(f'select 1 from document_document where id = {doc_id} for update;')

    @transaction.atomic
    def store_values_one_field_many_docs_no_ants(self,
                                                 field: DocumentField,
                                                 doc_ids_to_values: Dict[int, Any],
                                                 user: User = None):
        if not doc_ids_to_values:
            return
        if field.requires_text_annotations:
            raise Exception(
                f'Can not store values without annotations into a field requiring annotations: {field.code}')
        with connection.cursor() as cursor:
            for doc_id in doc_ids_to_values.keys():
                self.lock_document(cursor, doc_id)  # will unlock on transaction end
            FieldValue.objects.filter(document_id__in=doc_ids_to_values.keys(), field=field).delete()
            FieldAnnotation.objects.filter(document_id__in=doc_ids_to_values.keys(), field=field).delete()
            typed_field = TypedField.by(field)
            to_save = [FieldValue(document_id=doc_id,
                                  field=field,
                                  value=typed_field.field_value_python_to_json(v),
                                  modified_by=user) for doc_id, v in doc_ids_to_values.items()]
            FieldValue.objects.bulk_create(to_save)

    @transaction.atomic
    def store_values_one_doc_many_fields_no_ants(self,
                                                 doc: Document,
                                                 field_codes_to_python_values: Dict[str, Any],
                                                 user: User = None):
        if not field_codes_to_python_values:
            return

        with connection.cursor() as cursor:
            self.lock_document(cursor, doc.pk)  # will unlock on transaction end
            document_type = doc.document_type  # type: DocumentType

            all_fields = {f.code: f for f in DocumentField.objects.filter(document_type=document_type).all()}

            to_save = list()  # type: List[FieldValue]
            for field_code, python_val in field_codes_to_python_values.items():
                field = all_fields.get(field_code)  # type: DocumentField
                if not field:
                    raise Exception(f'Requested storing field {field_code} for document of type {document_type.code} '
                                    f'but this document type has no such field.')
                if field.requires_text_annotations:
                    raise Exception(f'Requested storing field value without annotation for field {field_code} '
                                    f'but this field requires annotations.')
                typed_field = TypedField.by(field)

                to_save.append(FieldValue(document=doc,
                                          field=field,
                                          value=typed_field.field_value_python_to_json(python_val),
                                          modified_by=user))

            FieldValue.objects.filter(document_id=doc.pk, field__code__in=field_codes_to_python_values.keys()).delete()
            FieldAnnotation.objects.filter(document_id=doc.pk,
                                           field__code__in=field_codes_to_python_values.keys()).delete()
            FieldValue.objects.bulk_create(to_save)

    @transaction.atomic
    def clear_field_value_no_false_match(self, document: Document, field: DocumentField):
        with connection.cursor() as cursor:
            self.lock_document(cursor, document.pk)  # will unlock on transaction end
            FieldValue.objects.filter(document=document, field=field).delete()
            FieldAnnotation.objects.filter(document=document, field=field).delete()

    @transaction.atomic
    def update_field_value_with_dto(self,
                                    document: Document,
                                    field: DocumentField,
                                    field_value_dto: FieldValueDTO,
                                    user: User = None) -> Tuple[FieldValue, List[FieldAnnotation]]:
        """
        Update (patch) field value and annotations of the specified document and field.
        Annotations are merged into the annotation set existing in the DB.
        If "user" is provided then the operation is assumed as executed by a user and existing annotations and
        values of single-value fields may be overwritten.
        If "user" is None then the only the existing annotation/values created by system (having modified_by = None)
        may be overwritten.

        Main usages:
        1. LoadDocumentWithFields task:
        Loads field values from json, stores them with the user specified to prevent their re-detection.
        2. apps/document/api
        Store field values entered by user.
        3. Field detection.
        Store detected fields, merge with user-entered data.
        4. SimilarDocumentsField
        Equal to field detection.

        Usage variants:
        1. Field detection, user = None
            multi-value:
                 annotations: append new annotations,
                              update annotations on the same location created by system,
                              keep annotations on the same locations created by users.
                 field values: merge old + new (build from annotations)
            single-value:
                 annotations: update annotations created by system
                              keep annotations created by user
                 field values: keep values created by user, overwrite values created by system

        2. API v1, user is assigned
            multi-value:
                 annotations: append new ones
                              update annotations on the same location created by either system or users
                 field values: merge old + new (build from annotations)
            single-value:
                 annotations: delete old ones having different locations (do not put to false-match),
                              update old ones on the same location
                              create new if no old ants on the same location
                 field_value: overwrite


        :param document
        :param field
        :param field_value_dto:
        :param user: If set to None then the existing user-entered values will not be kept and only old values
                     detected by system may be overwritten.
                     If set to a user then the existing user-entered values may be overwritten.

        :return: Tuple of:  actual field value model;
                            list of created/modified annotations of the field.
        """

        typed_field = TypedField.by(field)  # type: TypedField

        if field_value_dto:
            if not typed_field.is_json_field_value_ok(field_value_dto.field_value):
                raise BadValueForField(f'Value is not suitable for field {field.code} ({typed_field.type_code}):\n'
                                       f'{field_value_dto.field_value}')
            if field_value_dto.annotations:
                for ant_dto in field_value_dto.annotations:
                    if ant_dto and not typed_field.is_json_annotation_value_ok(ant_dto.annotation_value):
                        raise BadAnnotationValueForField(f'Value is not suitable for annotation of field {field.code} '
                                                         f'({typed_field.type_code}):\n'
                                                         f'{ant_dto.annotation_value}')

        with connection.cursor() as cursor:
            self.lock_document(cursor, document.pk)  # will unlock on transaction end

            if isinstance(typed_field, MultiValueField):
                ex_ants_by_loc = defaultdict(list)  # type: Dict[Tuple, List[FieldAnnotation]]
                for a in FieldAnnotation.objects.filter(document=document, field=field):
                    ex_ants_by_loc[(a.location_start, a.location_end)].append(a)
            else:
                ex_ant = FieldAnnotation.objects.filter(document=document, field=field).first()  # type: FieldAnnotation

            new_ant_dtos = field_value_dto.annotations or []

            good_annotations = []  # type: List[FieldAnnotation]
            new_annotations = []  # type: List[FieldAnnotation]

            for new_ant_dto in new_ant_dtos:

                # Try to find existing field annotation to update instead of deleting-recreating each time.
                # This is needed to avoid obsolete ID changes which may require frontend to reload too much data.

                ex_ant_used = False

                if isinstance(typed_field, MultiValueField):
                    # For multi-value fields we can have multiple annotations on the same locations with dif values.
                    # For this case we only searching for possibly existing ant with this location and value
                    # and update its user (modified_by) if required.
                    ex_ants = ex_ants_by_loc.get((new_ant_dto.location_in_doc_start, new_ant_dto.location_in_doc_end))
                    if ex_ants:
                        for a in ex_ants:
                            if a.value == new_ant_dto.annotation_value:
                                if user is not None and not a.is_user_value:
                                    a.modified_by = user
                                    a.save(update_fields={'modified_by', 'modified_date'})
                                good_annotations.append(a)
                                ex_ant_used = True
                                break
                else:
                    # For single-value fields there may be only one existing annotation.
                    # Update it if it needs updating.
                    if ex_ant:
                        if (user is not None or not ex_ant.is_user_value) \
                                and (ex_ant.value != new_ant_dto.annotation_value
                                     or ex_ant.location_start != new_ant_dto.location_in_doc_start
                                     or ex_ant.location_end != new_ant_dto.location_in_doc_end):
                            ex_ant.modified_by = user
                            ex_ant.value = new_ant_dto.annotation_value
                            ex_ant.location_start = new_ant_dto.location_in_doc_start
                            ex_ant.location_end = new_ant_dto.location_in_doc_end
                            ex_ant.location_text = document.full_text[new_ant_dto.location_in_doc_start
                                                                      :new_ant_dto.location_in_doc_end]
                            ex_ant.text_unit_id = self.find_text_unit_id_by_location(document,
                                                                                     field,
                                                                                     new_ant_dto.location_in_doc_start,
                                                                                     new_ant_dto.location_in_doc_end)
                            ex_ant.extraction_hint = new_ant_dto.extraction_hint_name

                            ex_ant.save()
                        ex_ant_used = True
                        good_annotations.append(ex_ant)

                if not ex_ant_used:
                    new_ant = FieldAnnotation(
                        modified_by=user,
                        document=document,
                        field=field,
                        value=new_ant_dto.annotation_value,
                        location_start=new_ant_dto.location_in_doc_start,
                        location_end=new_ant_dto.location_in_doc_end,
                        location_text=document.full_text[new_ant_dto.location_in_doc_start
                                                         :new_ant_dto.location_in_doc_end],
                        text_unit_id=self.find_text_unit_id_by_location(document,
                                                                        field,
                                                                        new_ant_dto.location_in_doc_start,
                                                                        new_ant_dto.location_in_doc_end),
                        extraction_hint=new_ant_dto.extraction_hint_name
                    )
                    new_annotations.append(new_ant)
                    good_annotations.append(new_ant)

                if not isinstance(typed_field, MultiValueField):
                    break

            if new_annotations:
                FieldAnnotation.objects.bulk_create(new_annotations)

            if not isinstance(typed_field, MultiValueField):
                FieldAnnotation.objects \
                    .filter(document=document, field=field) \
                    .exclude(pk__in={a.pk for a in good_annotations if a.pk is not None}) \
                    .delete()

            if good_annotations:
                if isinstance(typed_field, MultiValueField):
                    actual_ant_values = {a.pk: a.value for a in good_annotations}
                    field_value = typed_field \
                        .build_json_field_value_from_json_ant_values(list(actual_ant_values.values()))
                else:
                    field_value = good_annotations[0].value
            else:
                field_value = field_value_dto.field_value

            field_value_model, fv_created = FieldValue.objects \
                .get_or_create(document=document,
                               field=field,
                               defaults={'document': document,
                                         'field': field,
                                         'value': field_value,
                                         'modified_by': user
                                         })  # type: FieldValue, bool

            if not fv_created \
                    and field_value_model.value != field_value \
                    and (typed_field.multi_value or (user is not None or field_value_model.modified_by is None)):
                # For existing field value models requiring update -
                # we update only multi-value fields as their value is always build from merged annotations
                # or fields previously set by system
                # or fields previously set by users too - if we are updating as a user
                field_value_model.value = field_value
                field_value_model.modified_by = user
                field_value_model.save(update_fields={'value', 'modified_date', 'modified_by'})

            DocumentField.objects.set_dirty_for_value(field.pk,
                                                      document.document_type_id)

            # return the actual value
            return field_value_model, good_annotations

    @transaction.atomic
    def delete_hidden_field_values_if_needed(self,
                                             doc: Document,
                                             event_sender) -> Optional[Set[str]]:
        with connection.cursor() as cursor:
            self.lock_document(cursor, doc.pk)  # will unlock on transaction end
            if not doc.is_completed():
                return None
            hidden_field_ids, hidden_field_codes = self.get_hidden_field_ids_codes(doc)

            if hidden_field_ids:
                if FieldAnnotation.objects.filter(document=doc, field_id__in=hidden_field_ids).delete() \
                        or FieldValue.objects.filter(document=doc, field_id__in=hidden_field_ids).delete():
                    fire_hidden_fields_cleared(sender=event_sender, document=doc, field_codes=hidden_field_codes)

        return hidden_field_codes

    @transaction.atomic
    def delete_field_annotation_and_update_field_value(self,
                                                       ant_model: FieldAnnotation,
                                                       user: User) -> Tuple[Document, DocumentField, FieldAnnotation]:
        with connection.cursor() as cursor:
            doc = ant_model.document
            self.lock_document(cursor, doc.pk)  # will unlock on transaction end

            field = ant_model.field
            ant_model.delete()
            FieldAnnotationFalseMatch.objects.bulk_create([FieldAnnotationFalseMatch.make_from_annotation(ant_model)])

            typed_field = TypedField.by(field)

            ants = FieldAnnotation.objects.filter(document=doc, field=field)
            if isinstance(typed_field, MultiValueField):
                current_ant_values = [a.value for a in ants]
                self._update_multi_value_field_by_changing_annotations(doc=doc,
                                                                       typed_field=typed_field,
                                                                       current_ant_values=current_ant_values,
                                                                       added_ant_value=None,
                                                                       removed_ant_value=ant_model.value,
                                                                       modified_by=user)

            else:
                field_value = ant_model.value if not field.requires_text_annotations else None
                for a in ants:
                    a.delete()  # just a cleanup
                self._store_field_value(doc, field, field_value, user)
        return doc, field, ant_model

    @transaction.atomic
    def store_field_annotation_and_update_field_value(self,
                                                      ant_model: FieldAnnotation,
                                                      old_ant_value: Any) -> FieldAnnotation:
        with connection.cursor() as cursor:
            doc = ant_model.document
            self.lock_document(cursor, doc.pk)  # will unlock on transaction end
            field = ant_model.field
            typed_field = TypedField.by(field)

            if not typed_field.is_json_annotation_value_ok(ant_model.value):
                raise BadAnnotationValueForField(f'Annotation value {ant_model.value} is not '
                                                 f'suitable for field {field.code}')

            ants = {a.pk: a for a in FieldAnnotation.objects.filter(document_id=doc.pk, field=field)}

            if ant_model.pk is not None:
                old_model = ants.get(ant_model.pk)
                if not old_model:
                    raise NotFound(f'Annotation with id {ant_model.pk} of field {field.code} not found '
                                   f'for document {doc.name} (#{doc.pk})')

                if old_model.field_id != ant_model.field.pk:
                    raise ChangingFieldNotPermitted('Changing field on existing annotation is not permitted')
                if old_model.document_id != ant_model.document.pk:
                    raise ChangingDocumentNotPermitted('Changing document on existing annotation is not permitted')

            ant_model.save()

            if isinstance(typed_field, MultiValueField):
                added_ant_value = ant_model.value
                removed_ant_value = old_ant_value
                modified_by = ant_model.modified_by

                ants[ant_model.pk] = ant_model

                current_ant_values = [a.value for a in ants.values()]

                self._update_multi_value_field_by_changing_annotations(doc,
                                                                       typed_field,
                                                                       current_ant_values,
                                                                       added_ant_value,
                                                                       removed_ant_value,
                                                                       modified_by)
            else:
                self._store_field_value(doc, field, ant_model.value, ant_model.modified_by)
                for a in ants.values():
                    a.delete()

            return ant_model

    def _update_multi_value_field_by_changing_annotations(self,
                                                          doc: Document,
                                                          typed_field: MultiValueField,
                                                          current_ant_values: List,
                                                          added_ant_value: Any,
                                                          removed_ant_value: Any,
                                                          modified_by: User):
        # this field value makes sense only if there was no FieldValue object in the DB
        field_value_from_ants = typed_field.build_json_field_value_from_json_ant_values(current_ant_values)
        field_value_model, fv_created = FieldValue.objects \
            .get_or_create(document=doc,
                           field=typed_field.field,
                           defaults={'document': doc,
                                     'field': typed_field.field,
                                     'value': field_value_from_ants,
                                     'modified_by': modified_by
                                     })  # type: FieldValue, bool
        if not fv_created and field_value_model.value != field_value_from_ants:
            # If there is existing FieldValue in DB then we need to merge the old field value with the new one
            merged_field_value = typed_field \
                .update_field_value_by_changing_annotations(current_ant_values=current_ant_values,
                                                            old_field_value=field_value_model.value,
                                                            added_ant_value=added_ant_value,
                                                            removed_ant_value=removed_ant_value)
            field_value_model.value = merged_field_value
            field_value_model.modified_by = modified_by
            field_value_model.save(update_fields={'value', 'modified_date', 'modified_by'})

    def _store_field_value(self, doc, field, field_value, user) -> FieldValue:
        field_value_model, fv_created = FieldValue.objects \
            .get_or_create(document=doc,
                           field=field,
                           defaults={'document': doc,
                                     'field': field,
                                     'value': field_value,
                                     'modified_by': user
                                     })  # type: FieldValue, bool
        if not fv_created and field_value_model.value != field_value:
            field_value_model.value = field_value
            field_value_model.modified_by = user
            field_value_model.save(update_fields={'value', 'modified_date', 'modified_by'})
        return field_value_model

    @transaction.atomic
    def update_field_values(self,
                            doc: Document,
                            user: User,
                            fval_by_code: Dict[str, Any]) -> List[Tuple[DocumentField, FieldValue]]:

        res = list()
        with connection.cursor() as cursor:
            self.lock_document(cursor, doc.pk)  # will unlock on transaction end
            field_by_code = {f.code: f for f in DocumentField.objects.filter(document_type_id=doc.document_type_id)}
            deleting_ant_ids = []  # type:List[int]

            for field_code, value in fval_by_code.items():
                field = field_by_code[field_code]
                typed_field = TypedField.by(field)

                ex_ants = list(FieldAnnotation.objects.filter(
                    document_id=doc.pk, field=field))  # type:List[FieldAnnotation]

                # 1. Validate new field value.
                # If field requires annotation then there should be annotation matching the new field value.
                # 2. Save new field value.
                # 3. Delete annotations not matching the new field value.

                if not typed_field.is_there_annotation_matching_field_value(value, [a.value for a in ex_ants]):
                    raise NoExistingAnnotationMatchingNewFieldValue(f'Field {field_code} ({typed_field.type_code}) '
                                                                    f'expects an existing annnotation matching the '
                                                                    f'new value. Please assign an annotation first.')

                if not typed_field.is_json_field_value_ok(value):
                    raise BadValueForField(f'Wrong value format for field {field_code} ({typed_field.type_code}):\n'
                                           f'{str(value)}')

                field_value_model = self._store_field_value(doc, field, value, user)

                for ex_ant in ex_ants:
                    if not typed_field.annotation_value_matches_field_value(field_value=value,
                                                                            annotation_value=ex_ant.value):
                        deleting_ant_ids.append(ex_ant.pk)
                if deleting_ant_ids:
                    FieldAnnotation.objects.filter(pk__in=deleting_ant_ids).delete()
                res.append((field, field_value_model))
        return res

    def find_text_unit_id_by_location(self, doc: Document, field: DocumentField,
                                      location_start: int, location_end: int) -> Optional[int]:
        return TextUnit.objects.filter(
            document=doc,
            unit_type=field.text_unit_type,
            location_start__lte=location_end,
            location_end__gte=location_start).values_list('pk', flat=True).first()

    def get_annotation_stats_by_field_value(self, field_value: FieldValue) -> Dict[str, int]:
        return {str(val or ''): count
                for val, count in sql_query('select ant.value, count(ant.*) '
                                            'from document_fieldannotation ant '
                                            'where ant.document_id = %s and ant.field_id = %s group by ant.value',
                                            [field_value.document_id, field_value.field_id])}

    def get_annotation_stats_by_doc(self, document_id: int, field_codes_only: Set[str] = None) \
            -> Dict[str, Dict[str, int]]:

        params = [document_id]

        if field_codes_only:
            params.append(field_codes_only)
            field_codes_sql = 'and ant.field_code in %s'
        else:
            field_codes_sql = ''

        sql = f'''select f.code, ant.value, count(ant.*) 
                 from document_fieldannotation ant 
                 inner join document_documentfield f on ant.field_id = f.uid 
                 where ant.document_id = %s {field_codes_sql}
                 group by f.code, ant.value'''

        res = defaultdict(dict)
        for field_code, ant_val, count in sql_query(sql, params):
            res[field_code][str(ant_val or '')] = count

        return res

    def update_docs_assignee(self,
                             document_ids: Iterable[int],
                             assignee_id: int,
                             project_pk: int = 0) -> int:
        documents = \
            Document.objects.filter(project__pk=project_pk, pk__in=document_ids) if project_pk \
                else Document.objects.filter(pk__in=document_ids)

        ret = documents.update(assignee=assignee_id,
                               assign_date=datetime.datetime.now())
        return ret

    def replace_wrong_choice_options(self,
                                     field_id: int,
                                     old_to_new: Dict[str, str] = None,  # { 'Choice 1': 'Choice A', ... }
                                     new_choices: Set[str] = None,  # {'Choice A', 'Choice B', ...}
                                     misfit_action: str = 'BREAK') -> Dict[str, Any]:
        """
        :param field_id: DocumentField which values we are changing
        :param old_to_new: you either provide "old_to_new mapping": old defined (or stored) values to new ones
        :param new_choices: ... or "new_choices": the only allowed choices
        :param misfit_action: 'BREAK', or 'AUTO-REPLACE' or 'DELETE'
        :return: status - how many values deleted, updated etc
        """
        op_status = {'deleted': 0,
                     'updated': 0,
                     'errors': []}  # list to store error messages

        if not old_to_new and not new_choices:
            raise Exception('Neither "old_to_new" nor "new_choices" option was provided')

        stale_query = FieldValue.objects.filter(
            field__pk=field_id)  # .exclude(value__in=choices)
        field_values = stale_query.values_list('pk', 'document_id', 'value')

        fields_to_update = {}  # type: Dict[int, Any]  # pk: new_values
        new_choice_list = list(new_choices) if new_choices else []
        # field_id, doc_id, value
        ants_to_delete = []  # type:List[Tuple[int, int]]

        for field_id, doc_id, val in field_values:
            if type(val) is not list:
                # TODO: what should we do if values stored are incorrect?
                if isinstance(val, str):
                    val = [val]
                else:
                    continue
            new_val = val[:]
            for i in range(len(val)):
                item = val[i]
                if not isinstance(item, str):
                    item = str(item)  # TODO: remove in prod
                if new_choices:
                    if item in new_choices:
                        continue

                    if misfit_action == 'BREAK':
                        op_status['errors'].append(f'Value "{item}" was''t found in "new_choices" '
                                                   f'list, document: {doc_id}. Aborted.')
                        return op_status
                    if misfit_action == 'AUTO-REPLACE':
                        options = difflib.get_close_matches(item, new_choice_list)
                        option = options[0] if options else new_choice_list[0]
                        new_val[i] = option
                        fields_to_update[field_id] = new_val
                    elif misfit_action == 'DELETE':
                        new_val.remove(item)
                        fields_to_update[field_id] = new_val
                        ants_to_delete.append((field_id, doc_id,))
                else:
                    if item not in old_to_new:
                        continue
                    new_val[i] = old_to_new[item]
                    fields_to_update[field_id] = new_val

        # insert updated values
        if not fields_to_update:
            return op_status

        # delete annotations
        deleting_ant_fields = list(set([a[0] for a in ants_to_delete]))
        for ant_pack in chunks(ants_to_delete, 100):
            doc_ids = list(set([a[1] for a in ant_pack]))
            ants = FieldAnnotation.objects.filter(document_id__in=doc_ids,
                                                  field_id__in=deleting_ant_fields)
            for a in ants:  # type: FieldAnnotation
                try:
                    a.delete()
                except Exception as e:
                    op_status['errors'].append(f'Error while deleting field annotation in database: {e}')
                    return op_status

        # check what fields have no values now and should be deleted
        fields_to_delete = []
        ids_to_delete = [k for k in fields_to_update]
        for field_id in ids_to_delete:
            if not fields_to_update[field_id]:
                fields_to_delete.append(field_id)
                del fields_to_update[field_id]

        # ... and delete those field values
        for field_ids_pack in chunks(fields_to_delete, 100):
            try:
                FieldValue.objects.filter(pk__in=field_ids_pack).delete()
            except Exception as e:
                op_status['errors'].append(f'Error while deleting field values in database: {e}')
                return op_status
        op_status['deleted'] = len(fields_to_delete)

        field_ids = [k for k in fields_to_update]
        for field_ids_pack in chunks(field_ids, 500):
            fvals = FieldValue.objects.filter(pk__in=field_ids_pack)
            for fval in fvals:  # type: FieldValue
                fval.value = fields_to_update[fval.pk]
            try:
                bulk_update(fvals)
                op_status['updated'] = op_status['updated'] + len(field_ids_pack)
            except Exception as e:
                op_status['errors'].append(f'Error while updating field values in database: {e}')
                return op_status
        # update corresponding annotations
        return op_status

    def get_wrong_choice_options(self,
                                 updated_field: DocumentField,
                                 limit_result: int = 20) -> Tuple[int, List[Tuple[str, str, str, str]]]:
        """
        Finds what field values are not in listed options
        :param updated_field: DocumentField that is updated
        :return: <total_values>, [(<doc_name>,<doc_url>,<wrong_value>,<closest_option>), ...]
        """
        choices = DocumentField.parse_choice_values(updated_field.choices)
        choice_set = set(choices)
        stale_query = FieldValue.objects.filter(
            field__pk=updated_field.pk)  # .exclude(value__in=choices)

        wrong_vals = []  # type: List[Tuple[str, str, str, str]]
        field_values = stale_query.values_list('pk', 'document_id', 'value')
        has_more_values = False

        old_new_map = {}  # type:Dict[str, str]
        for _, doc_id, val in field_values:
            if type(val) is not list:
                # TODO: what should we do if values stored are incorrect?
                if isinstance(val, str):
                    val = [val]
                else:
                    continue

            for item in val:
                if not isinstance(item, str):
                    item = str(item)  # TODO: remove in prod
                if item in choice_set:
                    continue
                # find suggested option
                if item in old_new_map:
                    option = old_new_map[item]
                else:
                    options = difflib.get_close_matches(item, choices)
                    option = options[0] if options else choices[0]
                if len(wrong_vals) == limit_result:
                    has_more_values = True
                else:
                    wrong_vals.append((doc_id, '', item, option,))
            if has_more_values:
                break

        # replace document ids with document names
        if wrong_vals:
            doc_ids = set([d[0] for d in wrong_vals])
            doc_names = Document.all_objects.filter(pk__in=doc_ids).values_list(
                'pk', 'name', 'document_type_id', 'project_id')
            doc_names = {d[0]: (d[1], d[2], d[3]) for d in doc_names}
            for i in range(len(wrong_vals)):
                doc_data = doc_names.get(wrong_vals[i][0])
                if doc_data:
                    # doc_editor_url(document_type_code, project_id, document_id)
                    doc_url = doc_editor_url(doc_data[1], doc_data[2], wrong_vals[i][0])
                    doc_name = doc_data[0]
                    wrong_vals[i] = (doc_name, doc_url, wrong_vals[i][2], wrong_vals[i][3],)

        return has_more_values, wrong_vals
