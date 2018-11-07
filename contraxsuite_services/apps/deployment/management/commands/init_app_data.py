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

import io
import pathlib
import shutil
from os import listdir, mkdir, path
from tempfile import NamedTemporaryFile
from typing import Dict, Tuple, Any, Callable, Optional
from zipfile import ZipFile

import pandas as pd
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.timezone import now

from apps.deployment.app_data import load_courts, load_terms, load_geo_entities
from apps.document.models import DocumentType, DocumentField, DocumentTypeField
from apps.extract import dict_data_cache
from apps.extract.models import Court, Term, GeoEntity


def load_csv_files(zip_file: ZipFile, files: list) -> pd.DataFrame:
    df = pd.DataFrame()
    for file in files:
        csv = io.BytesIO(zip_file.read(file))
        df = df.append(pd.read_csv(csv))
    return df


def terms_loader(zip_file: ZipFile, files: list) -> None:
    if Term.objects.exists():
        print('Terms data already uploaded')
        return
    print('Uploading terms...')

    df = load_csv_files(zip_file, files)
    with transaction.atomic():
        terms_count = load_terms(df)

    print('Detected %d terms' % terms_count)
    print('Caching terms config for Locate tasks...')

    dict_data_cache.cache_term_stems()


def courts_loader(zip_file: ZipFile, files: list) -> None:
    if Court.objects.exists():
        print('Courts data already uploaded')
        return
    print('Uploading courts...')

    df = load_csv_files(zip_file, files)
    with transaction.atomic():
        courts_count = load_courts(df)

    print('Detected %d courts' % courts_count)
    print('Caching courts config for Locate tasks...')

    dict_data_cache.cache_court_config()


def geoentities_loader(zip_file: ZipFile, files: list) -> None:
    if GeoEntity.objects.exists():
        print('Geo config data already uploaded')
        return
    print('Uploading geo config ...')

    df = load_csv_files(zip_file, files)
    with transaction.atomic():
        geo_aliases_count, geo_entities_count = load_geo_entities(df)

    print('Total created: %d GeoAliases' % geo_aliases_count)
    print('Total created: %d GeoEntities' % geo_entities_count)
    print('Caching geo config for Locate tasks...')

    dict_data_cache.cache_geo_config()


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
    print('Uploading document data ...')

    zip_file = ZipFile(file_patch)
    for file_info in zip_file.infolist():
        data = zip_file.read(file_info)
        buf = io.StringIO()
        with NamedTemporaryFile(mode='wb', suffix='.json') as tmp_file:
            tmp_file.write(data)
            tmp_file.seek(0)
            call_command('loaddata', tmp_file.name, app_label='document', stdout=buf, interactive=False)
            buf.seek(0)
    DocumentTypeField.objects.update(dirty=False, training_finished=False)


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
