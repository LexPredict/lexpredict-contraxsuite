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
import io
import pathlib
import shutil
import traceback
from os import listdir, mkdir, path
from tempfile import NamedTemporaryFile
from typing import Dict, Tuple, Any, Callable, Optional, Type
from zipfile import ZipFile
import pandas as pd

# Django imports
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.timezone import now
from django.db import models

# Project imports
from apps.common.models import AppVar
from apps.deployment.app_data import load_courts, load_terms, load_geo_entities, get_terms_data_urls, load_terms_data, \
    get_courts_data_urls, load_courts_data, get_geoentities_data_urls, load_geoentities_data
from apps.document.models import DocumentType, DocumentField
from apps.extract import dict_data_cache
from apps.extract.models import Court, Term, GeoEntity

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.4/LICENSE"
__version__ = "1.1.8"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def load_csv_files(zip_file: ZipFile, files: list) -> pd.DataFrame:
    df = pd.DataFrame()
    for file in files:
        csv = io.BytesIO(zip_file.read(file))
        df = df.append(pd.read_csv(csv))
    return df


def load_terms_df(df: pd.DataFrame) -> None:

    with transaction.atomic():
        terms_count = load_terms(df)

    print('Detected %d terms' % terms_count)
    print('Caching terms config for Locate tasks...')

    dict_data_cache.cache_term_stems()


def load_courts_df(df: pd.DataFrame) -> None:
    with transaction.atomic():
        courts_count = load_courts(df)

    print('Detected %d courts' % courts_count)
    print('Caching courts config for Locate tasks...')

    dict_data_cache.cache_court_config()


def load_geoentities_df(df: pd.DataFrame) -> None:
    with transaction.atomic():
        geo_aliases_count, geo_entities_count = load_geo_entities(df)

    print('Total created: %d GeoAliases' % geo_aliases_count)
    print('Total created: %d GeoEntities' % geo_entities_count)
    print('Caching geo config for Locate tasks...')

    dict_data_cache.cache_geo_config()


def terms_loader(zip_file: ZipFile, files: list) -> None:
    if Term.objects.exists():
        print('Terms data already uploaded')
        return
    print('Uploading terms...')

    df = load_csv_files(zip_file, files)
    load_terms_df(df)


def courts_loader(zip_file: ZipFile, files: list) -> None:
    if Court.objects.exists():
        print('Courts data already uploaded')
        return
    print('Uploading courts...')

    df = load_csv_files(zip_file, files)
    load_courts_df(df)


def geoentities_loader(zip_file: ZipFile, files: list) -> None:
    if GeoEntity.objects.exists():
        print('Geo config data already uploaded')
        return
    print('Uploading geo config...')

    df = load_csv_files(zip_file, files)
    load_geoentities_df(df)


DICTIONARY_LOADER_BY_FILE_PREFIX = dict(
    terms=terms_loader,
    courts=courts_loader,
    geoentities=geoentities_loader
)


def dictionary_loader(file_patch: str) -> None:
    zip_file = ZipFile(file_patch)
    files_by_loader = dict()
    for file_info in zip_file.infolist():
        if file_info.filename.endswith('/'):
            continue
        for prefix, loader in DICTIONARY_LOADER_BY_FILE_PREFIX.items():
            if file_info.filename.startswith(prefix):
                files = files_by_loader.get(loader)
                if not files:
                    files = list()
                    files_by_loader[loader] = files
                files.append(file_info)
                break
    for loader, files in files_by_loader.items():
        loader(zip_file, files)


def document_loader(file_patch: str) -> None:
    initialized = False
    for document_type in DocumentType.objects.all()[:2]:
        if document_type.code != 'document.GenericDocument':
            initialized = True
            break
    initialized = initialized or DocumentField.objects.exists()
    if initialized:
        print('Document data already initialized')
        return
    print('Uploading document data...')

    zip_file = ZipFile(file_patch)
    for file_info in zip_file.infolist():
        data = zip_file.read(file_info)
        buf = io.StringIO()
        with NamedTemporaryFile(mode='wb', suffix='.json') as tmp_file:
            tmp_file.write(data)
            tmp_file.seek(0)
            call_command('loaddata', tmp_file.name, app_label='document', stdout=buf, interactive=False)
            buf.seek(0)
    DocumentField.objects.update(dirty=False, training_finished=False)


class Command(BaseCommand):
    help = 'Uploads application data from specified folder'

    loader_by_file_prefix = dict(
        document_data=document_loader,
        dict_data=dictionary_loader
    )

    def get_file_loader(self, file: str) -> Optional[Callable[[str], None]]:
        for prefix, loader in self.loader_by_file_prefix.items():
            if file.startswith(str(prefix)):
                return loader
        return None

    def add_arguments(self, parser) -> None:
        parser.add_argument('--data-dir', required=True, type=str)

    @classmethod
    def get_proceed_dir(cls, data_dir):
        proceed_dir = '{0}/processed/{1}'.format(data_dir, now().strftime('%Y-%m-%d_%H-%M-%S'))
        if not path.exists(proceed_dir):
            pathlib.Path(proceed_dir).parent.mkdir(parents=True, exist_ok=True)
            mkdir(proceed_dir)
        return proceed_dir

    @classmethod
    def init_dictionary_data(cls,
                             dictionary_name: str,
                             initialization_flag: AppVar,
                             dict_model: Type[models.Model],
                             urls: list,
                             data_loader: Callable[[str], pd.DataFrame],
                             df_loader: Callable[[pd.DataFrame], None]) -> None:
        if not initialization_flag.val:
            initialized = dict_model.objects.exists()
            if not initialized:
                print('Uploading {0}...'.format(dictionary_name))
                try:
                    df = pd.DataFrame()
                    for url in urls:
                        df = df.append(data_loader(url))
                    df_loader(df)
                    initialized = True
                except Exception:
                    print(traceback.print_exc())
            if initialized:
                initialization_flag.value = initialized
                initialization_flag.save()

    def handle(self, *args: Tuple, **options: Dict[Any, Any]) -> None:
        print('Uploading application data...')
        data_dir = options['data_dir']
        if not path.exists(data_dir):
            print('Data folder does not exist')

        for file in listdir(data_dir):
            if not path.isdir(file) and file.endswith('.zip'):
                print('Processing {0}...'.format(file))
                file_patch = '{0}/{1}'.format(data_dir, file)
                loader = self.get_file_loader(file)
                if loader:
                    loader(file_patch)
                shutil.move(file_patch, '{0}/{1}'.format(self.get_proceed_dir(data_dir), file))

        from apps.deployment.app_vars import DEPLOYMENT_TERMS_INITIALIZED, \
            DEPLOYMENT_COURTS_INITIALIZED, DEPLOYMENT_GEOENTITIES_INITIALIZED

        self.init_dictionary_data('terms',
                                  DEPLOYMENT_TERMS_INITIALIZED,
                                  Term,
                                  get_terms_data_urls(),
                                  load_terms_data,
                                  load_terms_df)

        self.init_dictionary_data('courts',
                                  DEPLOYMENT_COURTS_INITIALIZED,
                                  Court,
                                  get_courts_data_urls(),
                                  load_courts_data,
                                  load_courts_df)

        self.init_dictionary_data('geo config',
                                  DEPLOYMENT_GEOENTITIES_INITIALIZED,
                                  GeoEntity,
                                  get_geoentities_data_urls(),
                                  load_geoentities_data,
                                  load_geoentities_df)
