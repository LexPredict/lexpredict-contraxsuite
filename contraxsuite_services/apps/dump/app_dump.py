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

import logging
import sys
import traceback
from io import StringIO
from tempfile import NamedTemporaryFile
from typing import Any, Dict, Type, Callable

from allauth.account.models import EmailAddress, EmailConfirmation
from django.core import serializers as core_serializers
from django.core.management import call_command
from django.db.models import Subquery
from django.db.models import Model, QuerySet
from django.http import HttpResponse

# Project imports
from apps.common.models import ReviewStatus, ReviewStatusGroup, AppVar
from apps.common.plugins import collect_plugins_in_apps
from apps.deployment.models import Deployment
from apps.document.models import (
    DocumentField, DocumentType, DocumentFieldDetector, ExternalFieldValue,
    DocumentFieldCategory, DocumentFieldFamily)
from apps.extract.models import Court, GeoAlias, GeoEntity, GeoRelation, Party, Term
from apps.task.models import TaskConfig
from apps.users.models import User, Role

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.6.0/LICENSE"
__version__ = "1.6.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


APP_CONFIG_MODELS = {
    DocumentType: None,
    DocumentField: None,
    DocumentFieldDetector: None,
    DocumentFieldCategory: None,
    DocumentFieldFamily: None,
}  # type: Dict[Type[Model], Callable[[QuerySet], QuerySet]]

FULL_DUMP_MODELS = {User: None,
                    Role: None,
                    EmailAddress: None,
                    EmailConfirmation: None,
                    ReviewStatus: None,
                    ReviewStatusGroup: None,
                    AppVar: None,
                    Deployment: None,
                    TaskConfig: None,
                    Court: None,
                    GeoAlias: None,
                    GeoEntity: None,
                    GeoRelation: None,
                    Party: None,
                    Term: None}  # type: Dict[Type[Model], Callable[[QuerySet], QuerySet]]

FULL_DUMP_MODELS.update(APP_CONFIG_MODELS)


def default_object_handler(obj: Any) -> Any:
    return obj


def get_dump(filter_by_model: Dict[Type[Model], Callable] = None,
             object_handler_by_model: dict = None) -> str:
    object_handler_by_model = object_handler_by_model if object_handler_by_model is not None else {}
    objects = []
    for model, qs_filter in filter_by_model.items():
        handler = object_handler_by_model.get(model) or default_object_handler
        query_set = qs_filter(model.objects.get_queryset()) if qs_filter else model.objects.all()
        objects += [handler(obj) for obj in query_set]
    return core_serializers.serialize('json', objects)


def write_dump(file_name: str, json_data):
    with open(file_name, 'w') as f:
        f.write(json_data)


def get_full_dump() -> str:
    return get_dump(FULL_DUMP_MODELS)


def write_full_dump(file_name: str):
    write_dump(file_name, get_full_dump())


def clear_owner(obj: Any) -> Any:
    if hasattr(obj, 'created_by'):
        obj.created_by = None
    if hasattr(obj, 'modified_by'):
        obj.modified_by = None
    return obj


def get_app_config_dump(document_type_codes=None) -> str:
    object_handler_by_model = {DocumentField: clear_owner}
    filter_by_model = {}
    if document_type_codes:
        def document_field_filter(qs):
            return qs.filter(document_type__code__in=document_type_codes)

        category_document_type_field = document_field_filter(DocumentField.objects.get_queryset()) \
            .values_list('category__pk') \
            .distinct('category__pk') \
            .order_by('category__pk')

        field_family_document_type_field = document_field_filter(DocumentField.objects.get_queryset()) \
            .values_list('family__pk') \
            .distinct('family__pk') \
            .order_by('family__pk')

        filter_by_model = dict(APP_CONFIG_MODELS)

        filter_by_model.update({
            DocumentType: lambda qs: qs.filter(code__in=document_type_codes),
            DocumentField: document_field_filter,
            DocumentFieldDetector: lambda qs: qs.filter(field__document_type__code__in=document_type_codes),
            DocumentFieldCategory: lambda qs: qs.filter(pk__in=Subquery(category_document_type_field)),
            DocumentFieldFamily: lambda qs: qs.filter(pk__in=Subquery(field_family_document_type_field))
        })
    return get_dump(filter_by_model, object_handler_by_model)


def get_field_values_dump() -> str:
    import apps.document.repository.document_field_repository as dfr
    field_repo = dfr.DocumentFieldRepository()
    data = field_repo.get_annotated_values_for_dump()
    transfer_objects = [ExternalFieldValue(**i) for i in data]
    return core_serializers.serialize('json', transfer_objects)


def write_field_values_dump(file_name: str):
    write_dump(file_name, get_field_values_dump())


def get_model_fixture_dump(app_name, model_name, filter_options=None, indent=4):
    """
    Get Model objects dump
    :param app_name:
    :param model_name:
    :param filter_options:
    :return:
    """
    app_module = sys.modules['apps.{}.models'.format(app_name)]
    model = getattr(app_module, model_name)
    queryset = model.objects.all()
    if filter_options:
        queryset = queryset.filter(**filter_options)
    return core_serializers.serialize('json', queryset, indent=indent or None)


def download(data, file_name='dump', file_ext='json', content_type='application/json'):
    """
    :param data: data to store in file
    :param file_name: str
    :param file_ext: str - file extension
    :param content_type: str - content type
    :return:
    """
    response = HttpResponse(data, content_type=content_type)
    filename = '{}.{}'.format(file_name, file_ext)
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    response['Content-Length'] = len(response.content)
    response['filename'] = filename
    return response


def load_fixture_from_dump(data, mode='default'):
    """
    Load any fixtures from json data
    :param data: json file content
    :param mode: default - Install all, replace existing objects by id'),
                 soft - do not install if any objects already exists'),
                 partial - Install only new objects by id')],
    :return:
    """
    try:
        with NamedTemporaryFile(mode='w+b', suffix='.json') as f:
            f.write(data)
            f.flush()
            old_stdout = sys.stdout
            result = StringIO()
            sys.stdout = result
            if mode == 'soft':
                call_command('loadnewdata', f.name, skip_if_exists='any')
            elif mode == 'partial':
                call_command('loadnewdata', f.name, skip_if_exists='one')
            else:
                call_command('loaddata', f.name)
            sys.stdout = old_stdout
            result_string = result.getvalue()
        ret = {'status': 'success',
               'result': result_string}
    except Exception as e:
        tb = traceback.format_exc()
        ret = {'status': 'error',
               'log': str(e),
               'exception': tb}
    return ret


STR_APP_DUMP_MODELS = 'app_dump_models'
STR_APP_CONFIG_MODELS = 'APP_CONFIG_MODELS'
STR_FULL_DUMP_MODELS = 'FULL_DUMP_MODELS'


def _register_app_dump_models(plugin_attr_name: str, dst_collection: Dict[Type[Model], Callable]):
    app_dump_models = collect_plugins_in_apps(STR_APP_DUMP_MODELS, plugin_attr_name)
    for app_name, models in app_dump_models.items():
        try:
            models = dict(models)
            dst_collection.update(models)
        except Exception as e:
            logging.error(f'Unable to register app dump models from app {app_name}.\n'
                          'Check {app_name}.app_dump_models.{plugin_attr_name}', exc_info=e)


def register_pluggable_app_dump_models():
    _register_app_dump_models(STR_APP_CONFIG_MODELS, APP_CONFIG_MODELS)
    _register_app_dump_models(STR_FULL_DUMP_MODELS, FULL_DUMP_MODELS)

    logging.info('The following models will be exported in app config dumps:\n{0}'
                 .format('\n'.join(sorted({m.__name__ for m in APP_CONFIG_MODELS}))))
    logging.info('The following models will be exported in full app dumps (total cleanup dumps):\n{0}'
                 .format('\n'.join(sorted({m.__name__ for m in FULL_DUMP_MODELS}))))
