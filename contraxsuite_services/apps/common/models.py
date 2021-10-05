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
import pickle
from typing import Any, Optional, Tuple, Dict, List, Callable

# Django imports
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.search import SearchVectorField
from django.db import models, transaction, connection
from django.db.models import Count, Avg, Max, Case, When, IntegerField, UniqueConstraint
from django.db.models.base import ModelBase
from django.db.models.deletion import CASCADE, DO_NOTHING
from django.db.models.lookups import IContains, Contains, Lookup
from django.dispatch import receiver
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.db.models import Q
from django.utils import timezone

# Third-party imports
import pandas as pd
from rest_framework_tracking.models import APIRequestLog
from simple_history.models import HistoricalRecords

# Project imports
from typeguard import check_type

from apps.common import redis, signals
from apps.common.log_utils import ProcessLogger
from apps.common.logger import CsLogger
from apps.common.migration_utils import is_migration_in_process
from apps.common.model_utils.improved_django_json_encoder import ImprovedDjangoJSONEncoder
from apps.common.singleton import Singleton
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


is_migrating = is_migration_in_process()


class AppVarQuerySet(models.QuerySet):
    def delete(self):
        for args in self.values('category', 'name', 'project_id', 'access_type'):
            AppVarStorage.clear_key(**args)
        return super().delete()


class ProjectAppVar:
    # project-level app var data, used as DTO
    # the logic under getting and setting ProjectAppVar is too complex to implement on
    # API level
    def __init__(self,
                 category: str,
                 name: str,
                 access_type: str,
                 description: str = '',
                 value: Any = None,
                 use_system: bool = False,
                 system_value: Any = None):
        self.category = category
        self.name = name
        self.access_type = access_type
        self.description = description
        self.value = value
        self.use_system = use_system
        self.system_value = system_value

    def __str__(self):
        us_sys = ' [use system] ' if self.use_system else ''
        return f'{self.category}: {self.name}{us_sys}. value="{self.value}". system value="{self.system_value}"'

    def __repr__(self):
        return self.__str__()


class AppVarsCollection:
    # static class that
    APP_VARS: Dict[Tuple[str, str], 'AppVar'] = {}
    SYSTEM_ONLY_APP_VARS: Dict[Tuple[str, str], 'AppVar'] = {}

    @classmethod
    def store_app_var(cls,
                      category: str,
                      name: str,
                      value: Any,
                      description: str,
                      access_type: str,
                      system_only: bool,
                      target_type: Any = None,
                      parser: Callable[[str], Any] = None,
                      validator: Callable[[Any], None] = None):
        default_app_var = AppVar()
        default_app_var.category = category
        default_app_var.name = name
        default_app_var.description = description
        default_app_var.value = value
        default_app_var.access_type = access_type
        default_app_var.target_type = target_type
        default_app_var.parser = parser
        default_app_var.validator = validator
        cls.APP_VARS[(category, name)] = default_app_var

        if system_only:
            cls.SYSTEM_ONLY_APP_VARS[(category, name)] = default_app_var


class KnownAppVars:
    @classmethod
    def get_system_only_app_vars(cls) -> Dict[Tuple[str, str], 'AppVar']:
        return AppVarsCollection.SYSTEM_ONLY_APP_VARS

    @classmethod
    def find_app_var(cls, category: str, name: str) -> Optional['AppVar']:
        return AppVarsCollection.APP_VARS.get((category, name,))


class AppVarStorage:
    APP_VAR_CACHE_EXPIRES_SECONDS = 60 * 15

    @classmethod
    def val(cls,
            category: str,
            name: str,
            description: str,
            access_type: str,
            default_value: Any,
            project_id: Optional[int] = None) -> Any:

        # mock in migrating / test mode
        if cls._should_return_mock():
            return default_value

        # first, get the appvar value from cache
        stored = cls._read_cached(category, name, access_type, project_id)
        if stored:
            return stored

        # if the appvar is not cached - try to find it in the DB by full key
        db_values = cls._read_db_values(category, name, project_id)

        if project_id in db_values:
            # exact match in DB
            cls._cache(category, name, access_type, project_id, db_values[project_id])
            return db_values[project_id]

        if db_values:
            db_value = list(db_values.values())[0]
            # there's no such record in DB but there's a system level appvar stored
            # cache the value with the project_id provided even if the value is not specified on the
            # project's level in the DB
            cls._cache(category, name, access_type, project_id, db_value)
            return db_value

        # AppVar wasn't saved yet
        # the problem is - where is the default value we should store?
        model = AppVar()
        model.category = category
        model.name = name
        model.description = description
        model.access_type = access_type
        model.project_id = project_id
        model.date = timezone.now()
        model.value = default_value
        cls._save_app_var_db_record(model)
        cls._cache(category, name, access_type, project_id, default_value)
        return model.value

    @classmethod
    def set(cls,
            category: str,
            name: str,
            value: Any,
            description: str = '',
            access_type: str = 'auth',
            project_id: Optional[int] = None,
            overwrite: bool = False) -> 'AppVar':
        if cls._should_return_mock():
            mock: AppVar = AppVar()
            mock.category = category
            mock.name = name
            mock.value = value
            mock.project_id = project_id
            mock.description = description
            mock.access_type = access_type
            return mock

        AppVar.check_is_value_ok(category, name, value)

        obj: AppVar  # IDE can't defer the type of the unpacked variable
        created: bool
        obj, created = cls._check_app_var_in_db(
            category, description, name, access_type, project_id, value)

        if not created and overwrite:
            obj.value = value
            obj.access_type = access_type    # set access_type via admin site
            cls._save_app_var_db_record(obj)

        # force renew cached value
        cls._cache(category, name, access_type, project_id, obj.value)
        return obj

    @classmethod
    def get_project_app_vars(cls,
                             project_id: int,
                             user: User = None,
                             exclude_system_only: bool = True) -> List[ProjectAppVar]:
        # we need a full set of app vars here:
        # - those defined on system level
        # - and those defined for this particular project
        # we can't be sure all these values are cached so we just query the DB
        # TODO: the question is: what if an app var is not stored in the DB?
        if cls._should_return_mock():
            return []
        a_vars = cls._get_project_db_app_vars(project_id, user)
        var_by_name: Dict[Tuple[str, str], ProjectAppVar] = {}
        system_vars = None
        if exclude_system_only:
            system_vars = KnownAppVars.get_system_only_app_vars()

        for v in a_vars:  # type: AppVar
            is_system_var = v.project_id is None
            key = (v.category, v.name,)
            if system_vars is not None and key in system_vars:
                continue

            if key in var_by_name:
                p_var = var_by_name[key]
            else:
                p_var = ProjectAppVar(category=v.category, name=v.name, description=v.description, access_type=v.access_type)
                p_var.use_system = is_system_var
                var_by_name[key] = p_var
            p_var.description = p_var.description or v.description
            if not is_system_var:
                p_var.use_system = False
            field_value = 'system_value' if is_system_var else 'value'
            setattr(p_var, field_value, v.value)

        return list(var_by_name.values())

    @classmethod
    def apply_project_app_vars(cls,
                               project_id: int,
                               p_vars: List[ProjectAppVar],
                               user_id: Optional[int]) -> None:
        # we probably got here from project-appvars-PATCH request
        # first, delete project app vars with "use_system=True"
        # SIC: we don't update system values here
        system_vars = [v for v in p_vars if v.use_system]
        # delete in DB and clear in cache
        for v in system_vars:
            cls._delete_app_var_rows(project_id, v.category, v.name)
            cls.clear_key(v.category, v.name, v.access_type, project_id)

        # TODO: add a check that passed project app var has corresponding system app var to forbid hacker actions + admin access?

        # store per project app vars
        project_vars = [v for v in p_vars if not v.use_system]
        for v in project_vars:
            # cached_value = cls._read_cached(v.category, v.name, project_id)
            # if cached_value == v.value:
            #     continue
            # store the value in DB and cache the value
            db_var = AppVar()
            db_var.category = v.category
            db_var.name = v.name
            db_var.access_type = v.access_type
            db_var.description = v.description
            if not db_var.description:
                default_appvar = KnownAppVars.find_app_var(v.category, v.name)
                if default_appvar:
                    db_var.description = db_var.description or default_appvar.description or ''
            db_var.value = v.value
            db_var.user_id = user_id

            cls._save_app_var_in_db(
                db_var.category,
                db_var.description,
                db_var.name,
                db_var.access_type,
                project_id,
                db_var.value,
                db_var.user_id
            )
            # cache
            cls._cache(db_var.category, db_var.name, db_var.access_type, project_id, db_var.value)

    @classmethod
    def _get_project_db_app_vars(cls, project_id: int, user: User = None):
        qs = AppVar.objects.filter(Q(project_id__isnull=True) | Q(project_id=project_id))
        if user and not user.is_superuser:
            qs = qs.exclude(access_type='admin')    # TODO: figure out further if we should use secure things in proj.
        return list(qs)

    @classmethod
    def _should_return_mock(cls) -> bool:
        return is_migrating or settings.TEST_RUN_MODE

    @classmethod
    def _save_app_var_db_record(cls, app_var: 'AppVar'):
        app_var.save()

    @classmethod
    def _delete_app_var_rows(cls, project_id: int, category: str, name: str):
        AppVar.objects.filter(project_id=project_id, category=category, name=name).delete()

    @classmethod
    def _read_db_values(cls,
                        category: str,
                        name: str,
                        project_id: Optional[int]) -> Dict[Optional[int], Any]:
        search_conditions = Q(category=category, name=name, project_id__isnull=True)
        if project_id is not None:
            search_conditions |= Q(category=category, name=name, project_id=project_id)
        return dict(AppVar.objects.filter(search_conditions).values_list('project_id', 'value'))

    @classmethod
    def _save_app_var_in_db(cls,
                            category: str,
                            description: str,
                            name: str,
                            access_type: str,
                            project_id: Optional[int],
                            value: Any,
                            user_id: Optional[int] = None) -> Tuple['AppVar', bool]:
        return cls._get_or_update_app_var(category, description, name, access_type,
                                          project_id, value, user_id, True)

    @classmethod
    def _check_app_var_in_db(cls,
                             category: str,
                             description: str,
                             name: str,
                             access_type: str,
                             project_id: Optional[int],
                             value: Any,
                             user_id: Optional[int] = None) -> Tuple['AppVar', bool]:
        return cls._get_or_update_app_var(category, description, name, access_type,
                                          project_id, value, user_id, False)

    @classmethod
    def _get_or_update_app_var(
            cls,
            category: str,
            description: str,
            name: str,
            access_type: str,
            project_id: Optional[int],
            value: Any,
            user_id: Optional[int] = None,
            update_db_value: bool = False) -> Tuple['AppVar', bool]:
        routine = AppVar.objects.update_or_create if update_db_value else AppVar.objects.get_or_create
        try:
            obj, created = routine(
                defaults={'value': value, 'description': description, 'user_id': user_id, 'access_type': access_type},
                category=category,
                name=name,
                project_id=project_id)
            return obj, created
        except Exception as e:
            logger = CsLogger.get_django_logger()
            logger.error(f'''Error saving app var ([{category}:{name}], description: [{description}]. 
                value: [{value}]).\n{e}''')
            raise

    @classmethod
    def _cache(cls, category: str, name: str, access_type: str, project_id: Optional[int], value: Any):
        if project_id is None:
            # we also delete all project level cached values because
            # they might be derived from the system-level value
            cls.clear_cache_values(category, name, access_type)

        key = cls._make_cache_key(category, name, access_type, project_id)
        redis.push(key, value, ex=cls.APP_VAR_CACHE_EXPIRES_SECONDS)

    @classmethod
    def clear_cache_values(cls, category: str, name: str, access_type: str):
        key_pattern = cls._make_cache_key(category, name, access_type, None) + ':*'
        for key in redis.list_keys(key_pattern):
            key = key.decode('utf-8')
            redis.popd(key, False)

    @classmethod
    def _read_cached(cls, category: str, name: str, access_type: str, project_id: Optional[int]) -> Any:
        return redis.pop(cls._make_cache_key(category, name, access_type, project_id))

    @classmethod
    def _make_cache_key(cls,
                        category: str,
                        name: str,
                        access_type: str,
                        project_id: Optional[int] = None):
        if project_id is not None:
            return f'app_var:{category}:{name}:{access_type}:{project_id}'
        return f'app_var:{category}:{name}:{access_type}'

    @classmethod
    def clear_key(cls, category: str, name: str, access_type: str, project_id: Optional[int] = None):
        cache_key = cls._make_cache_key(category, name, access_type, project_id)
        redis.popd(cache_key)

    @classmethod
    def clear(cls, category: str, name: str, access_type: str, project_id: Optional[int] = None) -> Tuple[Any, Any]:
        # clear cache additionally in case if key exists in cache, but doesn't exist in DB
        cls.clear_key(category, name, access_type, project_id)
        return AppVar.objects.filter(category=category, name=name, project_id=project_id).delete()


class AppVar(models.Model):
    """
    Storage for application variables.
    """
    DEFAULT_CATEGORY: str = 'general'
    COMMON_CATEGORY: str = 'Common'
    DEPLOYMENT_CATEGORY: str = 'Deployment'
    DOCUMENT_CATEGORY: str = 'Document'
    EXTRACT_CATEGORY: str = 'Extract'
    NOTIFICATIONS_CATEGORY: str = 'Notifications'
    RAWDB_CATEGORY: str = 'RawDB'
    TASK_CATEGORY: str = 'Task'
    MAIL_CATEGORY: str = 'Mail server'
    ACCESS_TYPE_CHOICES = (('all', 'Available for all users'),
                           ('auth', 'Available for authenticated users '),
                           ('admin', 'Available for superusers / admins only'))

    class Meta:
        verbose_name: str = 'App Var'
        verbose_name_plural: str = 'App Vars'
        constraints = [
            UniqueConstraint(fields=['category', 'name', 'project'],
                             name='unique_with_project'),
            UniqueConstraint(fields=['category', 'name'],
                             condition=Q(project=None),
                             name='unique_without_project'),
        ]

    # variable category, unique together with name
    category = models.CharField(max_length=100, db_index=True, default=DEFAULT_CATEGORY)

    # variable name, unique together with category
    name = models.CharField(max_length=100, db_index=True)

    # variable data
    value = JSONField(blank=True, null=True)

    access_type = models.CharField(max_length=10, choices=ACCESS_TYPE_CHOICES, default='auth')

    # project-level configuration
    project = models.ForeignKey('project.Project', blank=True, null=True, on_delete=CASCADE, default=None)

    # variable description
    description = models.TextField(blank=True)

    # last modified date
    date = models.DateTimeField(auto_now=True, db_index=True)

    # last modified user
    user = models.ForeignKey(User, related_name="created_%(class)s_set", null=True, blank=True, db_index=True, on_delete=CASCADE)

    history = HistoricalRecords()

    objects = AppVarQuerySet.as_manager()

    # we use this field to test the provided value. We don't store "target_type" field in the DB
    target_type = None

    # parsing function: string -> target_type
    parser: Callable[[str], Any] = None

    # validating function: value -> None. Raises RuntimeError
    validator: Callable[[Any], None] = None

    def __str__(self):
        return f'App Variable (category={self.category} name={self.name} project={self.project})'

    def val(self, project_id: Optional[int] = None) -> Any:
        return AppVarStorage.val(
            self.category, self.name, self.description, self.access_type, self.value, project_id)

    @classmethod
    def set(cls,
            category: str,
            name: str,
            value: Any,
            description: str = '',
            access_type: str = 'auth',
            project_id: Optional[int] = None,
            system_only: bool = True,
            overwrite: bool = False,
            target_type: Any = None,
            parser: Callable[[str], Any] = None,
            validator: Callable[[Any], None] = None) -> 'AppVar':
        if target_type is None and value is not None:
            # infer target type from the app var default value
            target_type = type(value)
        AppVarsCollection.store_app_var(category, name, value, description,
                                        access_type, system_only,
                                        target_type, parser, validator)
        return AppVarStorage.set(category, name, value, description, access_type, project_id, overwrite)

    def delete(self, **kwargs):
        AppVarStorage.clear_key(self.category, self.name, self.access_type, self.project_id)
        return super().delete(**kwargs)

    def is_optional_value(self):
        if self.target_type is None:
            return False
        return hasattr(self.target_type, "__args__") and self.target_type.__args__[-1] is type(None)

    @classmethod
    def check_is_value_ok(cls, category: str, name: str, value: Any) -> None:
        app_var: Optional[AppVar] = KnownAppVars.find_app_var(category, name)
        if app_var:
            app_var._check_is_value_ok(value)

    def _check_is_value_ok(self, value: Any) -> None:
        if self.target_type is None:
            return

        if value is None:
            if not self.is_optional_value():
                raise RuntimeError(f'Null value is not allowed')
        try:
            check_type('value', value, self.target_type)
        except TypeError:
            val_type = 'None'
            if value is not None:
                val_type = type(value).__name__

            expected_type = self.target_type.__name__ if hasattr(self.target_type, '__name__') \
                else str(self.target_type)
            if 'typing.' in expected_type:
                expected_type = expected_type[len('typing.')]
            expected_type.strip('`')
            raise RuntimeError(f'Value provided is of type "{val_type}", expected type "{expected_type}"')

        if self.validator:
            self.validator(value)

    def try_cast_string(self, value_str: str) -> Any:
        """
        This method tries to cast passed string to the target type.
        The method may throw errors.
        """
        value = None
        if self.parser:
            value = self.parser(value_str)
        elif self.target_type is not None:
            value = self.target_type(value_str)

        if value is None and self.target_type is None:
            if not self.is_optional_value():
                raise RuntimeError(f'Null value is not allowed')
        return value


@receiver(models.signals.post_save, sender=AppVar)
def save_var(sender, instance, created, **kwargs):
    """
    Store created_by from request
    """
    if hasattr(instance, 'request_user'):
        models.signals.post_save.disconnect(save_var, sender=sender)
        if created:
            instance.user = instance.request_user
            instance.save()
        models.signals.post_save.connect(save_var, sender=sender)


class ReviewStatusGroup(models.Model):
    """
    ReviewStatusGroup object model
    """
    # Group verbose name
    name = models.CharField(unique=True, max_length=100, db_index=True)

    # Group code
    code = models.CharField(unique=True, max_length=100, db_index=True,
                            blank=True, null=True)

    # Group order number
    order = models.PositiveSmallIntegerField()

    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['order', 'name', 'code']
        verbose_name = 'Review Status Group'
        verbose_name_plural = 'Review Status Groups'

    def __str__(self):
        """"
        String representation
        """
        return f'ReviewStatusGroup (pk={self.pk}, name={self.name})'

    def save(self, **kwargs):
        if not self.code:
            self.code = self.name.lower().replace(' ', '_')
        return super().save(**kwargs)


class ReviewStatus(models.Model):
    """
    ReviewStatus object model
    """
    # Status verbose name
    name = models.CharField(unique=True, max_length=100, db_index=True)

    # Status code
    code = models.CharField(unique=True, max_length=100, db_index=True,
                            blank=True, null=True)

    # Status order number
    order = models.PositiveSmallIntegerField()

    # Status group
    group = models.ForeignKey(ReviewStatusGroup, blank=True, null=True, db_index=True, on_delete=CASCADE)

    # flag to detect f.e. whether we should recalculate fields for a document
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['order', 'name', 'code']
        verbose_name = 'Review Status'
        verbose_name_plural = 'Review Statuses'

    def __str__(self):
        """"
        String representation
        """
        return f'ReviewStatus (pk={self.pk}, name={self.name})'

    def _fire_saved(self, old_instance=None):
        signals.review_status_saved.send(self.__class__, user=None, instance=self, old_instance=old_instance)

    def save(self, **kwargs):
        if not self.code:
            self.code = self.name.lower().replace(' ', '_')
        old_instance = ReviewStatus.objects.filter(pk=self.pk).first()
        super().save(**kwargs)
        with transaction.atomic():
            transaction.on_commit(lambda: self._fire_saved(old_instance))

    @classmethod
    def initial_status(cls):
        if is_migrating or settings.TEST_RUN_MODE:
            return None
        try:
            return cls.objects.first()
        except cls.DoesNotExist:
            return None

    @classmethod
    def initial_status_pk(cls):
        status = cls.initial_status()
        return cls.initial_status().pk if status else None

    @property
    def is_final(self):
        if self.group:
            return not self.group.is_active


def get_default_status():
    return ReviewStatus.initial_status_pk()


class ObjectStorage(models.Model):

    class Meta:
        verbose_name = 'Object Storage'
        verbose_name_plural = 'Object Stores'

    key = models.CharField(max_length=100, primary_key=True, db_index=True)

    last_updated = models.DateTimeField(null=False, blank=False, default=now)

    data = models.BinaryField(null=True, blank=True)

    def get_obj(self):
        if not self.data:
            return None
        return pickle.loads(self.data)

    def set_obj(self, obj):
        self.data = pickle.dumps(obj)

    @staticmethod
    def update_or_create(key: str, value_obj):
        ObjectStorage.objects.update_or_create(key=key, defaults={'last_updated': now(),
                                                                  'data': pickle.dumps(value_obj)})


class Action(models.Model):
    # action name - mostly just human-readable short view action value like "Document Note Created"
    name = models.CharField(max_length=50, default='unknown', db_index=True)
    # verbose name / something more informative that just action name either action description
    message = models.TextField(blank=True, null=True, db_index=True)
    # view.action value: update, partial_update, create, list, retrieve, destroy, etc.
    view_action = models.CharField(max_length=50, blank=True, null=True, db_index=True)

    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, db_index=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, db_index=True)
    object_pk = models.CharField(max_length=36, blank=True, null=True, db_index=True)
    object = GenericForeignKey('content_type', 'object_pk')
    date = models.DateTimeField(auto_now=True, db_index=True)
    model_name = models.CharField(max_length=50, blank=True, null=True)
    app_label = models.CharField(max_length=20, blank=True, null=True)
    object_str = models.CharField(max_length=200, blank=True, null=True, db_index=True)
    request_data = JSONField(blank=True, null=True, encoder=ImprovedDjangoJSONEncoder)

    def __str__(self):
        return f'{self.user.name if self.user else "None"} - ' \
               f'{self.name} - ' \
               f'{self.model_name}#{self.object_pk} - ' \
               f'{self.date}'


class SQCount(models.Subquery):
    template = "(SELECT count(*) FROM (%(subquery)s) _count)"
    output_field = models.IntegerField()


class CustomAPIRequestLog(APIRequestLog):
    sql_log = models.TextField(null=True, blank=True)


class ThreadDumpRecord(models.Model):
    date = models.DateTimeField(auto_now=True, db_index=True)
    node = models.CharField(max_length=1024, blank=True, null=True, db_index=True)
    pid = models.IntegerField(null=True, blank=True)
    command_line = models.CharField(max_length=1024, blank=True, null=True, db_index=True)
    cpu_usage = models.FloatField(null=True, blank=True)
    cpu_usage_system_wide = models.FloatField(null=True, blank=True)
    memory_usage = models.BigIntegerField(null=True, blank=True)
    memory_usage_system_wide = models.BigIntegerField(null=True, blank=True)
    dump = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Thread Dump Record'
        verbose_name_plural = 'Thread Dump Records'


class MethodStats(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True, db_index=True)
    time = models.FloatField(db_index=True)

    # user-defined fields
    name = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    comment = models.CharField(max_length=200, blank=True, null=True)

    # method description
    # function name "get_json_data"
    method = models.CharField(max_length=200, db_index=True)
    # function path like "apps.common.decorators.callers"
    path = models.CharField(max_length=200, null=True, blank=True, db_index=True)
    # output of help(function)
    description = models.TextField(null=True, blank=True)
    # SQL logs
    sql_log = models.TextField(null=True, blank=True)
    # function args
    args = models.TextField(null=True, blank=True)
    # function kwargs
    kwargs = models.TextField(null=True, blank=True)
    # callers "... pdb.TerminalPdb.default  >> apps.common.decorators.callers'
    callers = models.TextField(null=True, blank=True)
    has_error = models.BooleanField(default=False)
    error_traceback = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Method Stat'
        verbose_name_plural = 'Method Stats'

    def __str__(self):
        body = '{} - {} - {}'.format(
            self.method,
            self.name,
            round(self.time, 5))
        if self.has_error:
            body += ', error'
        return body

    @classmethod
    def get(cls, as_dataframe: bool = True, **filter_kwargs):
        """
        Return grouped by method/name statistic with AVG time and N calls
        :param as_dataframe: bool - whether return pandas.dataframe or plain QuerySet
        :param filter_kwargs: positional arguments represents options for filter() qs method
        :return: pandas Dataframe OR QuerySet
        """
        # .filter(has_error=False)\
        qs = cls.objects \
            .values('method', 'path', 'name') \
            .annotate(calls=Count('id'),
                      errors=Count(Case(
                          When(has_error=True, then=1),
                          output_field=IntegerField(),
                      )),
                      avg_time=Avg('time'), max_time=Max('time')) \
            .filter(**filter_kwargs)
        qs = list(qs)
        qs.sort(key=lambda m: -m['calls'])
        if as_dataframe:
            return pd.DataFrame.from_records(qs, columns=['name', 'method',
                                                          'calls', 'errors',
                                                          'avg_time', 'max_time'])
        return qs


class MethodStatsCollectorPlugin(models.Model):
    path = models.CharField(
        max_length=200, db_index=True, unique=True,
        help_text='Full absolute path to a method like "apps.common.api.v1.AppVarsAPIView.get".')

    # user-defined fields
    name = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    comment = models.CharField(max_length=200, blank=True, null=True)

    # SQL logs
    log_sql = models.BooleanField(default=False)
    # how deep introspect to store a caller name, min is 3 for the decorator
    callers_depth = models.PositiveSmallIntegerField(default=5)
    # store batch of collected stats in N items
    batch_size = models.PositiveSmallIntegerField(default=10, blank=True, null=True)
    # store batch of collected stats in N seconds
    batch_time = models.PositiveSmallIntegerField(default=60, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Method Stats Collector Plug-in'

    def __str__(self):
        return '{} - {}'.format(self.path, self.name)


@receiver(models.signals.post_save, sender=MethodStatsCollectorPlugin)
def save_plugin(sender, instance, created, **kwargs):
    """
    Decorate chosen method
    """
    from apps.common.decorators import collect_stats, decorate, undecorate
    if not created:
        undecorate(path=instance.path)
    decorate(collect_stats, **MethodStatsCollectorPlugin.objects.filter(pk=instance.pk).values()[0])


@receiver(models.signals.post_delete, sender=MethodStatsCollectorPlugin)
def delete_plugin(sender, instance, **kwargs):
    """
    Un-decorate chosen method
    """
    from apps.common.decorators import undecorate
    try:
        undecorate(path=instance.path)
    except RuntimeError:
        # MethodStatsCollectorPlugin may have wrong "path", for example - but we
        # shouldn't prevent SQL record's deleting
        pass


class MenuGroup(models.Model):

    class Meta:
        verbose_name = 'Menu Group'
        verbose_name_plural = 'Menu Groups'

    name = models.CharField(
        max_length=100, db_index=True,
        help_text='Menu item group (folder) name.')

    public = models.BooleanField(default=False)

    # Group order number
    order = models.PositiveSmallIntegerField(default=0)

    user = models.ForeignKey(
        User, related_name="created_%(class)s_set", null=True, blank=True, db_index=True, on_delete=DO_NOTHING)

    def __str__(self):
        return '{}'.format(self.name)


@receiver(models.signals.post_save, sender=MenuGroup)
def save_menu_group(sender, instance, created, **kwargs):
    """
    Store created_by from request
    """
    if hasattr(instance, 'request_user'):
        models.signals.post_save.disconnect(save_menu_group, sender=sender)
        if created:
            instance.user = instance.request_user
            instance.save()
        models.signals.post_save.connect(save_menu_group, sender=sender)


class MenuItem(models.Model):

    class Meta:
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'

    name = models.CharField(
        max_length=100, db_index=True,
        help_text='Menu item name.')

    group = models.ForeignKey(MenuGroup, blank=True, null=True, on_delete=models.CASCADE)

    url = models.CharField(
        max_length=200, db_index=True,
        help_text='Menu item name.')

    public = models.BooleanField(default=False)

    # Group order number
    order = models.PositiveSmallIntegerField(default=0)

    user = models.ForeignKey(
        User, related_name="created_%(class)s_set", null=True, blank=True, db_index=True, on_delete=DO_NOTHING)

    def __str__(self):
        return '{} - {}'.format(self.group, self.name)


@receiver(models.signals.post_save, sender=MenuItem)
def save_menu_item(sender, instance, created, **kwargs):
    """
    Store created_by from request
    """
    if hasattr(instance, 'request_user'):
        models.signals.post_save.disconnect(save_menu_item, sender=sender)
        if created:
            instance.user = instance.request_user
            instance.save()
        models.signals.post_save.connect(save_menu_item, sender=sender)


########################
#     Model utils      #
########################


def approx_count(db_table_of_model):
    """
    Return approx db table total record count.
    Good enough if you don’t need the exact count.
    This value is updated by both autovacuum and autoanalyze,
    so it should never be much more than 10% off.
    :param db_table_of_model: str OR Model class
    :return: int
    """
    if isinstance(db_table_of_model, ModelBase):
        db_table = db_table_of_model._meta.db_table
    elif isinstance(db_table_of_model, str):
        db_table = db_table_of_model
    else:
        raise ValueError('Provide either str table name ot Model class.')
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT reltuples::bigint FROM pg_catalog.pg_class WHERE relname = '{db_table}';")
        return cursor.fetchone()[0]


class PostgresILike(IContains):
    """
    Make {column} ILIKE {value} query instead of default UPPER(column) LIKE UPPER(value)
    """
    lookup_name = 'ilike'

    def as_postgresql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return '%s ILIKE %s' % (lhs, rhs), params


class FullTextSearch(Lookup):
    """
    Query {text column} having corresponding {text column}_tsvector column
    Note: that {column}_tsvector should have GIN index for better performance
    """
    lookup_name = 'full_text_search'
    tsvector_column_suffix = '_tsvector'

    def get_fts_lookup(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)

        # patch column name representation
        column_name = lhs[:-1] + self.tsvector_column_suffix + lhs[-1:]

        # patch value representation
        query_value = ' & '.join(['<->'.join(i.strip('%').split()) for i in rhs_params])

        from apps.common.app_vars import PG_FULL_TEXT_SEARCH_LOCALE
        locale = PG_FULL_TEXT_SEARCH_LOCALE.val()
        return f"{column_name} @@ to_tsquery('pg_catalog.{locale}', '{query_value}')", []

    def as_postgresql(self, qn, connection):
        source_field = self.lhs.field
        model = source_field.model
        tsv_column_name = source_field.name + self.tsvector_column_suffix
        model_fields = {i.name: i for i in model._meta.fields}
        tsv_field = model_fields.get(tsv_column_name)

        if tsv_field is None or not isinstance(tsv_field, SearchVectorField):
            # raise RuntimeError('Model "{}" should have "{}" field.'.format(model, tsv_column_name))

            # fail silently - use insensitive contains search
            return IContains(self.lhs, self.rhs).as_sql(qn, connection)

        if source_field.name not in getattr(self.lhs.field.model, 'full_text_search_fields', []):
            # raise RuntimeError('Model "{}" should have "{}" in "{}" class atribute (List).'.format(
            #     model, 'full_text_search_fields', tsv_column_name))

            # fail silently - use insensitive contains search
            return IContains(self.lhs, self.rhs).as_sql(qn, connection)

        return self.get_fts_lookup(qn, connection)


class ContainsOrFullTextSearch(FullTextSearch):
    """
    Query {text column} having corresponding {text column}_tsvector column OR usual LIKE
    if USE_FULL_TEXT_SEARCH is False
    Note: that {column}_tsvector should have GIN index for better performance
    """
    lookup_name = 'contains'
    base_lookup_class = Contains

    def as_postgresql(self, qn, connection):
        if self.enable_full_text_search(qn) is True:
            try:
                return super().as_postgresql(qn, connection)
            except:
                # fail silently - get default lookup
                pass
        return self.base_lookup_class(self.lhs, self.rhs).as_sql(qn, connection)

    def enable_full_text_search(self, qn):
        from apps.common.app_vars import USE_FULL_TEXT_SEARCH, AUTO_FULL_TEXT_SEARCH_CUTOFF
        if USE_FULL_TEXT_SEARCH.val() == 'auto':
            target = qn.klass_info['model'] if qn.klass_info is not None else self.lhs.alias
            approx_table_rows = approx_count(target)
            return approx_table_rows > AUTO_FULL_TEXT_SEARCH_CUTOFF.val()
        return USE_FULL_TEXT_SEARCH.val()


class ExportFile(models.Model):

    class Meta:
        verbose_name = 'Export File'
        verbose_name_plural = 'Export Files'

    file_path = models.CharField(
        max_length=1024,
        db_index=True,
        help_text='File path')

    file_created = models.BooleanField(default=False, null=False)

    comment = models.CharField(
        max_length=1024,
        null=True,
        help_text='Comment on file')

    created_time = models.DateTimeField(null=False, blank=False)

    stored_time = models.DateTimeField(null=True, blank=True)

    expires_at = models.DateTimeField(null=False, blank=False, db_index=True)

    downloaded = models.BooleanField(default=False, null=False)

    email_sent = models.BooleanField(default=False, null=False)

    user = models.ForeignKey(User, db_index=True, null=True, on_delete=CASCADE)

    def get_link(self, abs_path=False, as_html=True):
        if not self.file_created:
            return ''
        uri = reverse('admin:download_file_data', args=[self.pk])
        if abs_path:
            uri = f'{settings.API_URL_PROTOCOL}://{settings.HOST_NAME}{uri}'
        if as_html:
            return mark_safe(f'<a href="{uri}">download</a>')
        return uri

    def send_email(self, log: ProcessLogger = None,
                   subject: str = None, text: str = None, html: str = None):
        from apps.notifications.notifications import send_email
        link = self.get_link(abs_path=True, as_html=False)
        default_subject = 'Document Files Ready to Download'
        default_msg_template = 'You can download your documents {}'
        default_text = default_msg_template.format(link)
        default_html = default_msg_template.format(f'<a href="{link}">here</a>')
        send_email(
            log=log or ProcessLogger(),
            dst_user=self.user,
            subject=subject or default_subject,
            txt=text or default_text,
            html=html or default_html,
            prevent_link_tracking=True)
        self.email_sent = True
        self.save()

    @classmethod
    def send_multi_file_email(cls,
                              file_refs: List['ExportFile'],
                              user: User,
                              log: ProcessLogger = None,
                              subject: str = None,
                              text: str = None,
                              html: str = None):
        from apps.notifications.notifications import send_email
        links = {d.file_path: d.get_link(abs_path=True, as_html=False) for d in file_refs}
        default_subject = 'Document Files Ready to Download'
        default_msg_template = 'Here you can download your documents:<br/>\n{}'

        links_text = '\n'.join([f'{links[r.file_path]}' for r in file_refs])
        links_markup = '<br/>\n'.join([f'<a href="{links[r.file_path]}">{r.comment}</a>' for r in file_refs])

        default_text = default_msg_template.format(links_text)
        default_html = default_msg_template.format(links_markup)
        send_email(
            log=log or ProcessLogger(),
            dst_user=user,
            subject=subject or default_subject,
            txt=text or default_text,
            html=html or default_html,
            prevent_link_tracking=True)
        for link in file_refs:
            link.email_sent = True
            link.save()


class IContainsOrFullTextSearch(ContainsOrFullTextSearch):
    lookup_name = 'icontains'
    base_lookup_class = IContains


models.CharField.register_lookup(PostgresILike)
models.CharField.register_lookup(FullTextSearch)

models.TextField.register_lookup(PostgresILike)
models.TextField.register_lookup(FullTextSearch)
models.TextField.register_lookup(ContainsOrFullTextSearch)
models.TextField.register_lookup(IContainsOrFullTextSearch)
