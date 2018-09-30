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

import sys
import traceback
from io import StringIO
from tempfile import NamedTemporaryFile

from allauth.account.models import EmailAddress, EmailConfirmation

from django.core import serializers as core_serializers
from django.core.management import call_command
from django.db.models import F
from django.http import HttpResponse


# Project imports
from apps.common.models import ReviewStatus, ReviewStatusGroup, AppVar
from apps.deployment.models import Deployment
from apps.document.models import (
    DocumentField, DocumentType, DocumentFieldDetector,
    DocumentFieldValue, ExternalFieldValue)
from apps.extract.models import Court, GeoAlias, GeoEntity, GeoRelation, Party, Term
from apps.task.models import TaskConfig
from apps.users.models import User, Role

MODELS_TO_DUMP = (User,
                  Role,
                  EmailAddress,
                  EmailConfirmation,
                  ReviewStatus,
                  ReviewStatusGroup,
                  DocumentField,
                  DocumentType,
                  DocumentFieldDetector,
                  AppVar,
                  Deployment,
                  TaskConfig,
                  Court,
                  GeoAlias,
                  GeoEntity,
                  GeoRelation,
                  Party,
                  Term)


def write_dump(file_name: str, json_data):
    with open(file_name, 'w') as f:
        f.write(json_data)


def get_full_dump():
    app_models = []
    for model in MODELS_TO_DUMP:
        app_models += list(model.objects.all())
    return core_serializers.serialize('json', app_models)


def write_full_dump(file_name: str):
    write_dump(file_name, get_full_dump())


def get_field_values_dump():
    data = DocumentFieldValue.objects \
        .filter(removed_by_user=False,
                created_by__isnull=False,
                sentence__text__isnull=False) \
        .annotate(type_id=F('document__document_type__pk'),
                  sentence_text=F('sentence__text')) \
        .values('type_id', 'field_id', 'value', 'extraction_hint',
                'sentence_text', 'created_date', 'modified_date')

    transfer_objects = [ExternalFieldValue(**i) for i in data]
    return core_serializers.serialize('json', transfer_objects)


def write_field_values_dump(file_name: str):
    write_dump(file_name, get_field_values_dump())


def get_model_fixture_dump(app_name, model_name, filter_options=None):
    """
    Get Model objects dump
    :param app_name:
    :param model_name:
    :param filter_options:
    :return:
    """
    module = sys.modules['apps.{}.models'.format(app_name)]
    model = getattr(module, model_name)
    queryset = model.objects.all()
    if filter_options:
        queryset = queryset.filter(**filter_options)
    return core_serializers.serialize('json', queryset)


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
                call_command('loadnewdata', f.name, skip_if_exists='any', interactive=False)
            elif mode == 'partial':
                call_command('loadnewdata', f.name, skip_if_exists='one', interactive=False)
            else:
                call_command('loaddata', f.name, interactive=False)
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
