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

# Standard imports
import json
import time
from uuid import UUID
from typing import Any, Callable, Iterable, List
from time import sleep

# Django imports
from django.core.serializers.base import DeserializedObject
from django.db import transaction
from django.core import serializers

# Project imports
import task_names
from apps.common.collection_utils import group_by
from apps.common.log_utils import ProcessLogger
from apps.document.field_types import TypedField
from apps.document.field_type_registry import FIELD_TYPE_REGISTRY
from apps.document.models import DocumentType, DocumentFieldDetector, DocumentField, \
    DocumentFieldCategory, DocumentFieldFamily
from apps.document.repository.document_field_repository import DocumentFieldRepository
from apps.document.scheme_migrations.scheme_migration import CURRENT_VERSION, SchemeMigration
from apps.task.models import Task
from apps.task.tasks import ExtendedTask, CeleryTaskLogger
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class ValidationError(Exception):
    pass


class ObjectHeap:
    def __init__(self):
        self._heap_by_object_class = {}

    def add_source_object(self, obj: Any) -> None:
        object_class = type(obj.object)
        heap = self._heap_by_object_class.get(object_class)
        if not heap:
            heap = {}
            self._heap_by_object_class[object_class] = heap
        heap[obj.pk] = obj

    def get_by_source_pk(self, object_class: type, object_pk: Any) -> Any:
        heap = self._heap_by_object_class.get(object_class)
        return heap.get(object_pk) if heap else None


class DeserializedObjectController:
    exept_m2m = []

    @classmethod
    def init_static(cls):
        pass

    def __init__(self, deserialized_object: DeserializedObject, auto_fix_validation_errors: bool,
                 logger: ProcessLogger = None):
        self._deserialized_object = deserialized_object
        self._auto_fix_validation_errors = auto_fix_validation_errors
        self._dependent_objects = []
        self._model_classes_save_order = None
        self._object_validators = []
        self._m2m_validators = []
        self._missed_object_validators = []
        self._logger = logger
        self._object_heap = None
        self.do_basic_cleanup()

    def do_basic_cleanup(self):
        pass

    @property
    def object(self) -> Any:
        return self._deserialized_object.object

    @property
    def pk(self) -> Any:
        return self.object.pk

    @property
    def auto_fix_validation_errors(self) -> bool:
        return self._auto_fix_validation_errors

    @property
    def model_name(self) -> str:
        return type(self.object).__name__

    def _execute_for_dependent_objects(self, predicate: Callable[[Any], None]) -> None:
        if self._model_classes_save_order:
            ordered_dependent_objects = [[] for i in range(len(self._model_classes_save_order) + 1)]
            for dependent_object in self._dependent_objects:
                for index, model_class in enumerate(self._model_classes_save_order):
                    if isinstance(dependent_object.object, model_class):
                        ordered_dependent_objects[index].append(dependent_object)
                        dependent_object = None
                        break
                if dependent_object:
                    ordered_dependent_objects[len(ordered_dependent_objects) - 1].append(dependent_object)
            for dependent_objects in ordered_dependent_objects:
                for dependent_object in dependent_objects:
                    predicate(dependent_object)
        else:
            for dependent_object in self._dependent_objects:
                predicate(dependent_object)

    def add_dependent_object(self, dependent_object: Any):
        self._dependent_objects.append(dependent_object)

    def set_object_heap(self, object_heap: ObjectHeap) -> None:
        self._object_heap = object_heap
        if object_heap:
            self._object_heap.add_source_object(self)
        self._execute_for_dependent_objects(lambda obj: obj.set_object_heap(self._object_heap))

    def get_deserialized_object_by_source_pk(self, object_class: type, source_pk: Any) -> Any:
        return self._object_heap.get_by_source_pk(object_class, source_pk)

    def _init(self) -> None:
        if not self._object_heap:
            self.set_object_heap(ObjectHeap())

    def _log_info(self, message: str) -> None:
        if self._logger:
            self._logger.info(message)

    def _set_save_order(self, model_classes: list) -> None:
        self._model_classes_save_order = model_classes

    def _run_validators(self, validators: list, context: dict) -> None:
        if self._auto_fix_validation_errors:
            return
        for validator in validators:
            validator(context)

    def _add_validation_errors(self, validators: Iterable, errors: list, context: dict) -> None:
        if self._auto_fix_validation_errors:
            return

        for validator in validators:
            try:
                validator(context)
            except Exception as exc:
                errors.append(exc)

    def _add_object_validator(self, validator: Callable[[dict], None]) -> None:
        self._object_validators.append(validator)

    def _get_save_object_context(self) -> dict:
        return {}

    def _add_m2m_validator(self, validator: Callable[[dict], None]) -> None:
        self._m2m_validators.append(validator)

    def _get_save_m2m_context(self) -> dict:
        return {}

    def _add_missed_object_validator(self, validator: Callable[[dict], None]) -> None:
        self._missed_object_validators.append(validator)

    def _get_clear_missed_object_context(self) -> dict:
        return {}

    def _save_deserialized_object(self, context: dict) -> None:
        self._deserialized_object.object.save()

    def _save_m2m(self, _context: dict) -> None:
        if self._deserialized_object.m2m_data:
            for accessor_name, object_list in self._deserialized_object.m2m_data.items():
                if accessor_name in self.exept_m2m:
                    continue
                getattr(self.object, accessor_name).set(object_list)
        self._deserialized_object.m2m_data = None

    def save_with_dependent_objects(self) -> None:
        self._log_info(f'Saving {self.model_name} #{self.pk} ...')
        context = self._get_save_object_context()
        self._run_validators(self._object_validators, context)
        self._save_deserialized_object(context)
        self._execute_for_dependent_objects(lambda obj: obj.save_with_dependent_objects())

    def save_m2m(self) -> None:
        self._log_info(f'Saving many to many relations for {self.model_name} #{self.pk} ...')
        context = self._get_save_m2m_context()
        self._run_validators(self._m2m_validators, context)
        self._save_m2m(context)
        self._execute_for_dependent_objects(lambda obj: obj.save_m2m())

    def clear_missed_objects(self) -> None:
        msg = f'Clearing objects missing in the config being imported for {self.model_name} #{self.pk} ...'
        self._log_info(msg)
        self._run_validators(self._missed_object_validators, self._get_clear_missed_object_context())
        self._execute_for_dependent_objects(lambda obj: obj.clear_missed_objects())

    def save(self) -> None:
        self._init()
        with transaction.atomic():
            self.clear_missed_objects()
            self.save_with_dependent_objects()
            self.save_m2m()

    def validate(self, errors: list = None) -> list:
        if errors is None:
            errors = []
        self._init()
        self._log_info(f'Validating {self.model_name} #{self.pk} ...')
        self._add_validation_errors(self._missed_object_validators, errors, self._get_clear_missed_object_context())
        self._add_validation_errors(self._object_validators, errors, self._get_save_object_context())
        self._add_validation_errors(self._m2m_validators, errors, self._get_save_m2m_context())

        self._execute_for_dependent_objects(lambda obj: obj.validate(errors))
        return errors

    @classmethod
    def to_str_if_uuid(cls, pk: Any) -> Any:
        return str(pk) if isinstance(pk, UUID) else pk

    def _filter_missed_objects(self, model_class: type, saved_objects: Iterable[dict]) -> list:
        saved_object_pks = set()
        pk_to_saved_object = {}
        for saved_object in saved_objects:
            pk = self.to_str_if_uuid(saved_object.get('pk'))
            pk_to_saved_object[pk] = saved_object
            saved_object_pks.add(pk)
        for dependent_object in self._dependent_objects:
            if isinstance(dependent_object.object, model_class):
                dependent_object_pk = self.to_str_if_uuid(dependent_object.pk)
                if dependent_object_pk in saved_object_pks:
                    saved_object_pks.remove(dependent_object_pk)
        return [pk_to_saved_object[pk] for pk in saved_object_pks]


class DeserializedDocumentFieldDetector(DeserializedObjectController):
    def __init__(self,
                 deserialized_object,
                 auto_fix_validation_errors: bool,
                 logger: ProcessLogger = None):
        super().__init__(deserialized_object, auto_fix_validation_errors, logger=logger)
        self._add_object_validator(lambda context: self._validate_field_changed())

    @property
    def object(self) -> DocumentFieldDetector:
        return super().object

    @property
    def field_pk(self) -> Any:
        return self.object.field_id

    def _validate_field_changed(self) -> None:
        for field_pk in DocumentFieldDetector.objects.filter(pk=self.pk).values_list('field__pk', flat=True):
            old_field_pk = self.to_str_if_uuid(field_pk)
            new_field_pk = self.to_str_if_uuid(self.field_pk)
            if old_field_pk != new_field_pk:
                err_msg = f'Unable to update field detector #{self.pk}. Field ' + \
                          f'has changed, old field id is #{old_field_pk}, ' + \
                          f'new field id is #{new_field_pk}'
                raise ValidationError(err_msg)


class DeserializedDocumentField(DeserializedObjectController):
    def __init__(self,
                 deserialized_object,
                 auto_fix_validation_errors: bool,
                 remove_missed_in_dump_objects: bool,
                 logger: ProcessLogger = None):
        super().__init__(deserialized_object, auto_fix_validation_errors, logger=logger)
        self._remove_missed_in_dump_objects = remove_missed_in_dump_objects
        self._add_object_validator(self._validate_critical_properties_changed)
        self._add_object_validator(self._validate_choice_values_removed)
        self._add_missed_object_validator(lambda _: self._clear_missed_field_detectors(save=False))

    def do_basic_cleanup(self):
        document_field = self._deserialized_object.object  # type: DocumentField
        document_field.modified_by = None
        document_field.created_by = None

    @property
    def object(self) -> DocumentField:
        return super().object

    @classmethod
    def _get_document_type_pk(cls, obj) -> Any:
        return obj.document_type_id

    @property
    def document_type_pk(self) -> Any:
        return self._get_document_type_pk(self.object)

    @property
    def category_pk(self) -> Any:
        return self.object.category_id

    @category_pk.setter
    def category_pk(self, category_pk: Any) -> None:
        self.object.category_id = category_pk

    @property
    def family_pk(self) -> Any:
        return self.object.family_id

    @family_pk.setter
    def family_pk(self, family_pk: Any) -> None:
        self.object.family_id = family_pk

    def _get_save_object_context(self) -> dict:
        saved_field = None
        for document_field in DocumentField.objects.filter(pk=self.pk):
            saved_field = document_field
        return {'saved_field': saved_field}

    @classmethod
    def _get_saved_field(cls, context: dict) -> DocumentField:
        return context.get('saved_field')

    @classmethod
    def _get_detected_values_count(cls, values_total: int, user_values_count: int) -> int:
        detected_values_count = values_total - user_values_count
        return detected_values_count if detected_values_count > 0 else 0

    @classmethod
    def _get_field_type_title(cls, field_type_code: str) -> str:
        field_type_title = field_type_code
        if field_type_code is not None:
            field_type_class = FIELD_TYPE_REGISTRY[field_type_code]
            field_type_title = field_type_class.title if field_type_class is not None else field_type_code
        return field_type_title

    def _validate_critical_properties_changed(self, context: dict) -> None:
        import apps.document.repository.document_field_repository as dfr
        field_repo = dfr.DocumentFieldRepository()

        saved_field = self._get_saved_field(context)
        if not saved_field:
            return
        err_msg = ''
        new_field_type = self.object.type
        old_document_type_pk = self.to_str_if_uuid(self._get_document_type_pk(saved_field))
        new_document_type_pk = self.to_str_if_uuid(self.document_type_pk)
        old_field_type = saved_field.type
        if old_document_type_pk != new_document_type_pk:
            err_msg += f'Document type has changed, old document type id is #{old_document_type_pk}' + \
                       f', new document type id is #{self.document_type_pk}. '
        if old_field_type != new_field_type:
            err_msg += 'Field type has changed, old field type is ' + \
                       f'"{self._get_field_type_title(old_field_type)}", ' + \
                       f'new field type is "{self._get_field_type_title(new_field_type)}". '
        if err_msg:
            err_msg = f'Unable to update field #{self.pk} "{self.object.code}". {err_msg}'
            values_count = field_repo.get_count_by_field(self.object.pk)
            user_values_count = 0
            detected_values_count = 0
            if values_count > 0:
                user_values_count = field_repo.get_doc_field_values_filtered_count(self.object.pk)
                detected_values_count = self._get_detected_values_count(values_count, user_values_count)
            err_msg += 'Existing document field values become invalid and will be removed. ' + \
                       f'User entered values {user_values_count}, ' + \
                       f'automatically detected values {detected_values_count}. ' + \
                       'You need to set force auto-fixes option to continue ' + \
                       '(this option will remove all values for this field) or make manual updates.'

            raise ValidationError(err_msg)

    def _get_invalid_choices(self, saved_field: DocumentField) -> set:
        old_choices = set(saved_field.get_choice_values())
        for choice_value in self.object.get_choice_values():
            if choice_value in old_choices:
                old_choices.remove(choice_value)
        return old_choices

    def _is_allow_values_not_specified_in_choices_was_unset(self, saved_field: DocumentField) -> bool:
        return saved_field.allow_values_not_specified_in_choices \
               and not self.object.allow_values_not_specified_in_choices

    def _validate_choice_values_removed(self, context: dict) -> None:
        saved_field = self._get_saved_field(context)
        if not saved_field or not TypedField.by(saved_field).is_choice_field \
                or not TypedField.by(self.object).is_choice_field:
            return
        err_msg = ''
        invalid_choices = self._get_invalid_choices(saved_field)
        if self._is_allow_values_not_specified_in_choices_was_unset(saved_field):
            err_msg += '"Allow values not specified in choices" flag is unset in the the config being imported. '
        if invalid_choices:
            invalid_choices = [f'"{invalid_choice}"' for invalid_choice in invalid_choices]
            err_msg += 'The following choice values are missing in ' + \
                       f'the config being imported: {", ".join(invalid_choices)}.'

        if err_msg:
            invalid_values_count = self.object.get_invalid_choice_annotations().count()
            user_values_count = 0
            detected_values_count = 0
            if invalid_values_count > 0:
                field_repo = DocumentFieldRepository()
                user_values_count = field_repo.get_invalid_choice_vals_count(self.object)
                detected_values_count = self._get_detected_values_count(invalid_values_count, user_values_count)
            err_msg += f'Number of invalid values: user entered values {user_values_count}, ' + \
                       f'automatically detected values {detected_values_count}. ' + \
                       'You need to set force auto-fixes option to continue (this option will remove all invalid ' + \
                       'values) or make manual updates.'
            err_msg = f'Unable to update field #{self.pk} "{self.object.code}". {err_msg}'
            raise ValidationError(err_msg)

    def _get_missed_field_detectors(self) -> list:
        missed_field_detectors_qs = DocumentFieldDetector.objects.filter(field=self.object).values('pk')
        return self._filter_missed_objects(DocumentFieldDetector, missed_field_detectors_qs)

    def _clear_missed_field_detectors(self, save=False) -> None:
        remove_missed_field_detectors = self._remove_missed_in_dump_objects and save
        missed_field_detectors = None
        if not self.auto_fix_validation_errors or remove_missed_field_detectors:
            missed_field_detectors = self._get_missed_field_detectors()
            # To exclude wrong error messages that field detector is missing but actually it was moved
            if not self.auto_fix_validation_errors:
                not_existing_field_detectors = []
                for field_detector in missed_field_detectors:
                    deserialized_field = None
                    field_detector_pk = UUID(field_detector['pk'])
                    deserialized_field_detector = self.get_deserialized_object_by_source_pk(DocumentFieldDetector,
                                                                                            field_detector_pk)
                    if deserialized_field_detector is not None:
                        field_pk = deserialized_field_detector.field_pk
                        deserialized_field = self.get_deserialized_object_by_source_pk(DocumentField, field_pk)
                    if deserialized_field is None:
                        not_existing_field_detectors.append(field_detector)
                missed_field_detectors = not_existing_field_detectors

        if not missed_field_detectors:
            return

        if not self.auto_fix_validation_errors:
            missed_field_detectors = [f'#{field_detector["pk"]}' for field_detector in missed_field_detectors]
            err_msg = 'The following field detectors are missing (field ' + \
                      f'#{self.object.pk} "{self.object.code}") in the config being imported: ' + \
                      f'{", ".join(missed_field_detectors)}. Please set force ' + \
                      'auto-fixes option to continue or solve this problem manually.'
            raise ValidationError(err_msg)

        if remove_missed_field_detectors:
            missed_field_detectors = [field_detector.get('pk') for field_detector in missed_field_detectors]
            DocumentFieldDetector.objects.filter(pk__in=missed_field_detectors).delete()

    def _save_deserialized_object(self, context: dict) -> None:
        saved_field = self._get_saved_field(context)
        if self.category_pk is not None:
            self.category_pk = self.get_deserialized_object_by_source_pk(DocumentFieldCategory, self.category_pk).pk
        if self.family_pk is not None:
            self.family_pk = self.get_deserialized_object_by_source_pk(DocumentFieldFamily, self.family_pk).pk

        conflicting_field = DocumentField.objects \
            .filter(document_type_id=self.document_type_pk, code=self.object.code) \
            .exclude(pk=self.pk) \
            .first()
        if conflicting_field is not None:
            err_msg = f'Unable to save document field #{self.pk} "{self.object.code}". ' + \
                      f'Database already contains a document field #{conflicting_field.pk} ' + \
                      f'with code "{conflicting_field.code}"'
            raise RuntimeError(err_msg)

        super()._save_deserialized_object(context)

        if saved_field and (self._is_allow_values_not_specified_in_choices_was_unset(saved_field) or
                            self._get_invalid_choices(saved_field)):
            self.object.get_invalid_choice_annotations().delete()

    def clear_missed_objects(self) -> None:
        super().clear_missed_objects()
        self._clear_missed_field_detectors(save=True)


class DeserializedDocumentType(DeserializedObjectController):
    exept_m2m = ['managers']

    def __init__(self,
                 deserialized_object: DeserializedObject,
                 auto_fix_validation_errors: bool,
                 remove_missed_in_dump_objects: bool,
                 logger: ProcessLogger = None):
        super().__init__(deserialized_object, auto_fix_validation_errors, logger=logger)
        self._auto_fix_validation_errors = auto_fix_validation_errors
        self._remove_missed_in_dump_objects = remove_missed_in_dump_objects
        self._set_save_order([DocumentFieldCategory, DocumentFieldFamily, DocumentField])
        self._add_missed_object_validator(lambda context: self._clear_missed_fields(save=False))

    def do_basic_cleanup(self):
        document_type = self._deserialized_object.object  # type: DocumentType
        document_type.modified_by = None
        document_type.created_by = None

    @property
    def object(self) -> DocumentType:
        return super().object

    def _get_missed_fields(self) -> list:
        missed_fields_qs = DocumentField.objects.filter(document_type=self.object).values('pk', 'code')
        return self._filter_missed_objects(DocumentField, missed_fields_qs)

    def _clear_missed_fields(self, save=False) -> None:
        remove_missed_fields = self._remove_missed_in_dump_objects and save
        missed_fields = None
        if not self.auto_fix_validation_errors or remove_missed_fields:
            missed_fields = self._get_missed_fields()
        if not missed_fields:
            return

        if not self.auto_fix_validation_errors:
            missed_fields = [f'#{field["pk"]} "{field["code"]}"' for field in missed_fields]
            err_msg = 'The following fields are missing in the config being imported: ' + \
                      f'{", ".join(missed_fields)}. Please set force ' + \
                      'auto-fixes option to continue or solve this problem manually.'
            raise ValidationError(err_msg)

        if remove_missed_fields:
            missed_fields = [missed_field.get('pk') for missed_field in missed_fields]
            DocumentField.objects.filter(pk__in=missed_fields).delete()

    def clear_missed_objects(self) -> None:
        super().clear_missed_objects()
        self._clear_missed_fields(save=True)


class DeserializedDocumentFieldCategory(DeserializedObjectController):
    saved_doc_types = set()

    @classmethod
    def init_static(cls):
        cls.saved_doc_types = set(DocumentType.objects.values_list('pk', flat=True))

    def __init__(self, deserialized_object, auto_fix_validation_errors: bool, logger: ProcessLogger = None):
        super().__init__(deserialized_object, auto_fix_validation_errors, logger=logger)
        saved_category_pk = None
        for category_pk in DocumentFieldCategory.objects \
                .filter(export_key=self.object.export_key) \
                .values_list('pk', flat=True):
            saved_category_pk = category_pk
        self._target_object_pk = saved_category_pk

    @property
    def object(self) -> DocumentFieldCategory:
        return super().object

    @property
    def document_type_id(self) -> Any:
        return self.object.document_type_id

    @document_type_id.setter
    def document_type_id(self, category_pk: Any) -> None:
        self.object.document_type_id = category_pk

    def _save_deserialized_object(self, context: dict) -> None:
        self.object.pk = self._target_object_pk
        if self.document_type_id is not None:
            importing_doc_type = self.get_deserialized_object_by_source_pk(
                DocumentType, self.document_type_id)
            if not importing_doc_type:
                # referenced doc type may not be stored on the server
                if self.document_type_id not in self.saved_doc_types:
                    self.document_type_id = None

        super()._save_deserialized_object(context)


class DeserializedDocumentFieldFamily(DeserializedObjectController):

    def __init__(self, deserialized_object, auto_fix_validation_errors: bool, logger: ProcessLogger = None):
        super().__init__(deserialized_object, auto_fix_validation_errors, logger=logger)
        saved_family_pk = None
        for family_pk in DocumentFieldFamily.objects \
                .filter(code=self.object.code) \
                .values_list('pk', flat=True):
            saved_family_pk = family_pk
        self._target_object_pk = saved_family_pk

    @property
    def object(self) -> DocumentFieldFamily:
        return super().object

    def _save_deserialized_object(self, context: dict) -> None:
        self.object.pk = self._target_object_pk
        super()._save_deserialized_object(context)


def get_import_conflicting_tasks_running(own_task_id: str) -> List[str]:
    tasks = Task.objects \
        .get_active_user_tasks() \
        .exclude(pk=own_task_id) \
        .exclude(name__in=[task_names.TASK_NAME_REFRESH_MATERIALIZED_VIEW,
                           task_names.TASK_NAME_CLEAN_ALL_TASKS,
                           task_names.TASK_NAME_CHECK_EMAIL_POOL]) \
        .distinct('name') \
        .order_by('name') \
        .values_list('name', flat=True)

    return list(tasks)


def import_document_type(json_bytes: bytes,
                         save: bool,
                         auto_fix_validation_errors: bool,
                         remove_missed_in_dump_objects: bool,
                         source_version: int,
                         task: ExtendedTask) -> DocumentType:
    conflicts = []
    for _ in range(2):
        conflicts = get_import_conflicting_tasks_running(task.task.pk)
        if not conflicts:
            break
        time.sleep(2)
    if conflicts:
        msg = f'The following user tasks are running: {", ".join(conflicts)}. ' + \
              'This import can cause their crashing because of document ' + \
              'type / field structure changes.'
        raise RuntimeError(msg)

    # check data contains version
    json_str = json_bytes.decode('utf-8')
    json_dict = json.loads(json_str)

    sm = SchemeMigration()
    if isinstance(json_dict, dict):
        # {"version":"75","data":[{"model": ... ]}
        version = json_dict.get('version')
        records = sm.migrate_model_records(json_dict['data'], int(version), CURRENT_VERSION)
        json_str = json.dumps(records)
    elif source_version != CURRENT_VERSION:
        json_str = sm.migrate_json(json_str, source_version, CURRENT_VERSION)

    for doc_type_subclass in DESERIALIZED_OBJECT_CLASSES:
        doc_type_subclass.init_static()

    objects = serializers.deserialize("json", json_str)
    document_type = None
    pk_to_field = {}
    field_detectors = []
    other_objects = []
    user = User.objects.get(id=task.task.user_id)
    logger = CeleryTaskLogger(task)
    for deserialized_object in objects:
        obj = deserialized_object.object
        if isinstance(obj, DocumentType):
            if document_type is not None:
                raise RuntimeError('More than one document types was detected')
            document_type = DeserializedDocumentType(deserialized_object,
                                                     auto_fix_validation_errors=auto_fix_validation_errors,
                                                     remove_missed_in_dump_objects=remove_missed_in_dump_objects,
                                                     logger=logger)
            document_type.object.created_by = user
            document_type.object.modified_by = user
            document_type.object.request_user = user

        elif isinstance(obj, DocumentField):
            field = DeserializedDocumentField(deserialized_object,
                                              auto_fix_validation_errors=auto_fix_validation_errors,
                                              remove_missed_in_dump_objects=remove_missed_in_dump_objects,
                                              logger=logger)
            field.object.created_by = user
            field.object.modified_by = user
            field.object.request_user = user

            pk_to_field[field.pk] = field
        elif isinstance(obj, DocumentFieldDetector):
            field_detector = DeserializedDocumentFieldDetector(deserialized_object,
                                                               auto_fix_validation_errors=auto_fix_validation_errors,
                                                               logger=logger)
            field_detector.object.request_user = user
            field_detectors.append(field_detector)
        elif isinstance(obj, DocumentFieldCategory):
            category = DeserializedDocumentFieldCategory(deserialized_object,
                                                         auto_fix_validation_errors=auto_fix_validation_errors,
                                                         logger=logger)
            category.object.request_user = user
            other_objects.append(category)
        elif isinstance(obj, DocumentFieldFamily):
            family = DeserializedDocumentFieldFamily(deserialized_object,
                                                     auto_fix_validation_errors=auto_fix_validation_errors,
                                                     logger=logger)
            family.object.request_user = user
            other_objects.append(family)
        else:
            raise RuntimeError('Unknown model')

    if document_type is None:
        raise RuntimeError('Unable to find document type')

    reconcile_doc_type(other_objects, document_type)

    conflicting_document_type = DocumentType.objects \
        .filter(code=document_type.object.code) \
        .exclude(pk=document_type.pk) \
        .first()
    if conflicting_document_type is not None:
        err_msg = f'Unable to import document type #{document_type.pk} "{document_type.object.code}". ' +\
                  f'Database already contains a document type #{conflicting_document_type.pk} ' + \
                  f'with code "{conflicting_document_type.code}"'
        raise RuntimeError(err_msg)

    for field_detector in field_detectors:
        field = pk_to_field.get(field_detector.field_pk)
        if field is not None:
            field.add_dependent_object(field_detector)
        else:
            raise RuntimeError(f'Unknown field #{field_detector.field_pk}')

    for field in pk_to_field.values():
        if field.document_type_pk == document_type.pk:
            document_type.add_dependent_object(field)
        else:
            raise RuntimeError(f'Unknown document type #{document_type.pk}')

    for obj in other_objects:
        document_type.add_dependent_object(obj)

    logger.info(f'Validation of {document_type.object.code} ...')
    validation_errors = document_type.validate()
    logger.info(f'Validation of {document_type.object.code} is finished')
    if validation_errors:
        task.log_error(f'{len(validation_errors)} VALIDATION ERRORS HAS OCCURRED DURING VALIDATION OF {document_type.object.code}.')
        for index, validation_error in enumerate(validation_errors):
            # for different timestamps
            sleep(0.001)
            task.log_error(f'VALIDATION ERROR {index + 1}. {validation_error}')
        raise ValidationError(f'Validation errors has occurred during import of {document_type.object.code}')

    if save:
        logger.info(f'Import of {document_type.object.code} ...')
        with transaction.atomic():
            document_type.save()
        logger.info(f'Import of {document_type.object.code} is finished')

    return document_type.object


def reconcile_doc_type(other_objects: List[Any], document_type: DocumentType):
    obj_by_class = group_by(other_objects, type)
    categories = obj_by_class.get(DeserializedDocumentFieldCategory, [])
    for cat in categories:  # type: DeserializedDocumentFieldCategory
        cat.document_type_id = document_type.pk


DESERIALIZED_OBJECT_CLASSES = [
    DeserializedDocumentFieldDetector,
    DeserializedDocumentField,
    DeserializedDocumentType,
    DeserializedDocumentFieldCategory,
    DeserializedDocumentFieldFamily
]
