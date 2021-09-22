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

from collections import defaultdict
from typing import Dict, List, Set, Optional, Any
import time

from django.db import models
from django.db.models import F
from django.dispatch import receiver

from apps.common import redis
from apps.document.models import DocumentType
from apps.extract.models import TermTag, CompanyTypeTag
from apps.rawdb.constants import FT_COMMON_FILTER, FT_USER_DOC_GRID_CONFIG, \
    FIELD_CODES_SHOW_BY_DEFAULT_NON_GENERIC, FIELD_CODES_SHOW_BY_DEFAULT_GENERIC, \
    FIELD_CODES_HIDE_FROM_CONFIG_API, FIELD_CODES_HIDE_BY_DEFAULT
from apps.rawdb.field_value_tables import get_columns
from apps.rawdb.models import SavedFilter
from apps.rawdb.rawdb.rawdb_field_handlers import ColumnDesc
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class SystemRawDBConfig:
    CACHE_EXPIRES_SECONDS = 60

    @classmethod
    def invalidate_cache(cls):
        for add_query_syntax in [True, False]:
            cache_key = f'SystemRawDBConfig_{add_query_syntax}'
            redis.popd(cache_key)

    @classmethod
    def get_config(cls,
                   add_query_syntax: bool = False,
                   user: Optional[User] = None) -> Dict[str, Any]:
        start = time.time()
        conf = cls._get_cached_config(add_query_syntax)
        # filter records by user Id
        conf['user_doc_grid_configs_by_project'] = cls._filter_records_by_user(
            conf['user_doc_grid_configs_by_project'], user)
        conf['common_filters_by_project'] = cls._filter_records_by_user(
            conf['common_filters_by_project'], user)
        conf['common_filters_by_document_type'] = cls._filter_records_by_user(
            conf['common_filters_by_document_type'], user)
        conf['time'] = time.time() - start
        return conf

    @classmethod
    def _filter_records_by_user(cls, records: Dict[str, Any], user: Optional[User]) -> Dict[str, Any]:
        filtered = {}
        for key in records:
            record = records[key]
            if user and record['user_id'] != user.pk and record['user_id'] is not None:
                continue
            del record['user_id']
            filtered[key] = record
        return filtered

    @classmethod
    def _get_cached_config(cls, add_query_syntax: bool) -> Dict[str, Any]:
        cache_key = f'SystemRawDBConfig_{add_query_syntax}'
        conf = redis.pop(cache_key)
        if not conf:
            conf = cls._get_actual_config(add_query_syntax)
            redis.push(cache_key, conf, ex=cls.CACHE_EXPIRES_SECONDS)
        return conf

    @classmethod
    def _get_actual_config(cls,
                           add_query_syntax: bool = False) -> Dict[str, Any]:
        start = time.time()
        document_type_schema = {}
        for document_type in DocumentType.objects.all():
            columns = get_columns(document_type,
                                  include_generic=document_type.is_generic(),
                                  is_select=True)  # type: List[ColumnDesc]
            columns = [c for c in columns if c.field_code not in FIELD_CODES_HIDE_FROM_CONFIG_API]

            system_fields = FIELD_CODES_SHOW_BY_DEFAULT_GENERIC \
                if document_type.is_generic() else FIELD_CODES_SHOW_BY_DEFAULT_NON_GENERIC
            search_fields = set(document_type.search_fields.values_list('code', flat=True))

            default_columns = {c.name for c in columns
                               if c.field_code not in FIELD_CODES_HIDE_FROM_CONFIG_API and
                               c.field_code not in FIELD_CODES_HIDE_BY_DEFAULT and
                               (c.field_code in system_fields or c.field_code in search_fields)}

            document_type_schema[document_type.code] = cls._document_type_schema_to_dto(
                document_type, columns, default_columns, add_query_syntax)

        common_filters_by_document_type = defaultdict(list)  # type: Dict[List]

        for document_type_code, filter_id, title, display_order, user_id in SavedFilter.objects \
                .filter(project_id__isnull=True, filter_type=FT_COMMON_FILTER) \
                .values_list('document_type__code', 'id', 'title', 'display_order', 'user_id'):
            common_filters_by_document_type[document_type_code].append({
                'id': filter_id,
                'title': title,
                'display_order': display_order,
                'user_id': user_id
            })

        common_filters_by_project = defaultdict(list)  # type: Dict[List]

        for project_id, filter_id, title, display_order, user_id in SavedFilter.objects \
                .filter(project_id__isnull=False, filter_type=FT_COMMON_FILTER) \
                .values_list('project_id', 'id', 'title', 'display_order', 'user_id'):
            common_filters_by_project[project_id].append({
                'id': filter_id,
                'title': title,
                'display_order': display_order,
                'user_id': user_id
            })

        user_doc_grid_configs_by_project = defaultdict(list)  # type: Dict[List]

        for project_id, columns, column_filters, order_by, user_id in SavedFilter.objects \
                .filter(project_id__isnull=False, filter_type=FT_USER_DOC_GRID_CONFIG) \
                .filter(document_type_id=F('project__type_id')) \
                .order_by('pk') \
                .values_list('project_id', 'columns', 'column_filters', 'order_by', 'user_id'):
            user_doc_grid_configs_by_project[project_id] = {
                'columns': columns,
                'column_filters': column_filters,
                'order_by': order_by,
                'user_id': user_id
            }

        term_tags = TermTag.objects.values_list('pk', 'name')
        companytype_tags = CompanyTypeTag.objects.values_list('pk', 'name')
        return {
            'document_type_schema': document_type_schema,
            'common_filters_by_document_type': common_filters_by_document_type,
            'common_filters_by_project': common_filters_by_project,
            'user_doc_grid_configs_by_project': user_doc_grid_configs_by_project,
            'time': time.time() - start,
            'term_tags': [{'id': i, 'name': n} for i, n in term_tags],
            'companytype_tags': [{'id': i, 'name': n} for i, n in companytype_tags],
        }

    @classmethod
    def _document_type_schema_to_dto(
            cls,
            document_type: DocumentType,
            columns: List[ColumnDesc],
            default_columns: Set[str],
            add_query_syntax: bool = False) -> Dict:
        document_type_data = {
            'code': document_type.code,
            'title': document_type.title,
            'columns': [cls._column_to_dto(column, add_query_syntax) for column in columns],
            'default_columns': default_columns
        }

        return document_type_data

    @classmethod
    def _column_to_dto(cls, column: ColumnDesc, add_query_syntax: bool = False) -> Dict:
        res = {
            'column': column.name,
            'title': column.title,
            'type': column.value_type.value,
        }
        if add_query_syntax:
            res['query_syntax'] = column.get_field_filter_syntax_hint()
        return res


@receiver(models.signals.post_save, sender=DocumentType)
def save_document_type(sender, instance, created, **kwargs):
    # invalidate RawDB cache
    SystemRawDBConfig.invalidate_cache()
