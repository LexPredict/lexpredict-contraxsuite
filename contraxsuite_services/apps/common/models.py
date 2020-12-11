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
from typing import Dict, Any

# Django imports
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.search import SearchVectorField
from django.db import models, transaction, connection
from django.db.models import Count, Avg, Max, Case, When, IntegerField
from django.db.models.base import ModelBase
from django.db.models.deletion import CASCADE, DO_NOTHING
from django.db.models.lookups import IContains, Contains, Lookup
from django.dispatch import receiver
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.timezone import now

# Third-party imports
import pandas as pd
from rest_framework_tracking.models import APIRequestLog
from simple_history.models import HistoricalRecords

# Project imports
from apps.common import redis, signals
from apps.common.log_utils import ProcessLogger
from apps.common.migration_utils import is_migration_in_process
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


is_migrating = is_migration_in_process()


class AppVar(models.Model):
    DEFAULT_CATEGORY = 'general'
    COMMON_CATEGORY = 'Common'
    DEPLOYMENT_CATEGORY = 'Deployment'
    DOCUMENT_CATEGORY = 'Document'
    EXTRACT_CATEGORY = 'Extract'
    NOTIFICATIONS_CATEGORY = 'Notifications'
    RAWDB_CATEGORY = 'RawDB'
    TASK_CATEGORY = 'Task'
    MAIL_CATEGORY = 'Mail server'

    """Storage for application variables"""

    class Meta:
        unique_together = (('category', 'name'),)

    # variable category, unique together with name
    category = models.CharField(max_length=100, db_index=True, default=DEFAULT_CATEGORY)

    # variable name, unique together with category
    name = models.CharField(max_length=100, db_index=True)

    # variable data
    value = JSONField(blank=True, null=True)

    # variable description
    description = models.TextField(blank=True)

    # last modified date
    date = models.DateTimeField(auto_now=True, db_index=True)

    # last modified user
    user = models.ForeignKey(
        User, related_name="created_%(class)s_set", null=True, blank=True, db_index=True, on_delete=CASCADE)

    history = HistoricalRecords()

    def __str__(self):
        return f"App Variable (category={self.category} name={self.name})"

    @classmethod
    def get_values_by_category(cls, category: str) -> Dict[str, Any]:
        if is_migrating:
            return {}
        cat_vals = {}
        for name, value in AppVar.objects.filter(category=category).values_list('name', 'value'):
            cat_vals[name] = value
        return cat_vals

    def get_cached_value(self, cache: Dict[str, Any]) -> Any:
        if self.name in cache:
            return cache[self.name]
        return self.val

    @property
    def cache_key(self):
        return f'app_var:{self.category}:{self.name}'

    def cache(self):
        redis.push(self.cache_key, self.value)

    @classmethod
    def set(cls, category: str, name: str, value, description='', overwrite=False) -> 'AppVar':
        if is_migrating or settings.TEST_RUN_MODE:
            mock = AppVar()
            mock.category = category
            mock.name = name
            mock.value = value
            mock.description = description
            return mock

        obj, created = cls.objects.get_or_create(
            category=category,
            name=name,
            defaults={"value": value, "description": description})
        if not created and overwrite:
            obj.value = value
            obj.save()

        # force renew cached value
        obj.cache()
        return obj

    @classmethod
    def get(cls, category: str, name: str, default=None):
        if is_migrating or settings.TEST_RUN_MODE:
            return default
        qs = cls.objects.filter(name=name, category=category)
        for v in qs.values_list('value', flat=True):
            return v
        return default

    @property
    def val(self):
        if is_migrating or settings.TEST_RUN_MODE:
            return self.value
        if redis.exists(self.cache_key) is True:
            return redis.pop(self.cache_key)
        try:
            self.refresh_from_db()
        except AppVar.DoesNotExist:
            self.save()
        self.cache()
        return self.value

    def save(self, **kwargs):
        res = super().save(**kwargs)
        self.cache()
        return res

    @classmethod
    def clear(cls, name: str, category: str):
        return cls.objects.filter(name=name, category=category).delete()


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

    def __str__(self):
        """"
        String representation
        """
        return "ReviewStatusGroup (pk={0}, name={1})" \
            .format(self.pk, self.name)

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
        verbose_name_plural = 'Review Statuses'

    def __str__(self):
        """"
        String representation
        """
        return "ReviewStatus (pk={0}, name={1})" \
            .format(self.pk, self.name)

    def _fire_saved(self, old_instance=None):
        signals.review_status_saved.send(self.__class__, user=None, instance=self, old_instance=old_instance)

    def save(self, **kwargs):
        if not self.code:
            self.code = self.name.lower().replace(' ', '_')
        old_instance = ReviewStatus.objects.filter(pk=self.pk).first()
        res = super().save(**kwargs)
        with transaction.atomic():
            transaction.on_commit(lambda: self._fire_saved(old_instance))
        return res

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


def get_default_status():
    return ReviewStatus.initial_status_pk()


class ObjectStorage(models.Model):
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
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, default='list')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_pk = models.CharField(max_length=36, blank=True, null=True)
    object = GenericForeignKey('content_type', 'object_pk')
    date = models.DateTimeField(auto_now=True)
    model_name = models.CharField(max_length=50, blank=True, null=True)
    app_label = models.CharField(max_length=20, blank=True, null=True)
    object_str = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return '{} - {} - {} - {}'.format(
            self.user.username,
            self.name,
            self.object or self.content_type.model.capitalize(),
            self.date)

    def save(self, **kwargs):
        self.model_name = self.content_type.model_class().__name__
        self.app_label = self.content_type.app_label
        self.object_str = None
        if self.object_pk:
            self.object_str = str(self.object)
        return super().save(**kwargs)


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
        locale = PG_FULL_TEXT_SEARCH_LOCALE.val
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
        if USE_FULL_TEXT_SEARCH.val == 'auto':
            target = qn.klass_info['model'] if qn.klass_info is not None else self.lhs.alias
            approx_table_rows = approx_count(target)
            return approx_table_rows > AUTO_FULL_TEXT_SEARCH_CUTOFF.val
        return USE_FULL_TEXT_SEARCH.val


class ExportFile(models.Model):
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
            html=html or default_html)
        self.email_sent = True
        self.save()


class IContainsOrFullTextSearch(ContainsOrFullTextSearch):
    lookup_name = 'icontains'
    base_lookup_class = IContains


models.CharField.register_lookup(PostgresILike)
models.CharField.register_lookup(FullTextSearch)

models.TextField.register_lookup(PostgresILike)
models.TextField.register_lookup(FullTextSearch)
models.TextField.register_lookup(ContainsOrFullTextSearch)
models.TextField.register_lookup(IContainsOrFullTextSearch)
