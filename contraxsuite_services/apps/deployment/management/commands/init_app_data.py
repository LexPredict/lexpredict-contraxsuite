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

# Project imports
from apps.common.models import AppVar
from apps.deployment.app_data import load_courts, load_terms, load_geo_entities, get_terms_data_urls, \
    get_courts_data_urls, get_geoentities_data_urls, load_df
from apps.document.models import DocumentType, DocumentField
from apps.extract import dict_data_cache
from apps.extract.models import Court, Term, GeoEntity

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.4/LICENSE"
__version__ = "1.2.2"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class DataLoader:
    def __init__(self, initialization_flag: AppVar = None):
        self.initialization_flag = initialization_flag

    def load(self) -> None:
        raise RuntimeError('Not implemented')

    def load_once(self) -> None:
        if not self.initialization_flag or not self.initialization_flag.val:
            try:
                self.load()
            except Exception:
                print(traceback.print_exc())
                return
            if self.initialization_flag:
                self.initialization_flag.value = True
                self.initialization_flag.save()
        else:
            print('Data is already initialized. Reset {0} flag to repeat initialization'
                  .format(self.initialization_flag.name))


class ZipFileLoader(DataLoader):
    def __init__(self, zip_file: ZipFile = None, files: list = None, initialization_flag: AppVar = None):
        super().__init__(initialization_flag)
        self.zip_file = zip_file
        self.files = files

    def load_df(self) -> pd.DataFrame:
        df = pd.DataFrame()
        for file in self.files:
            csv = io.BytesIO(self.zip_file.read(file))
            df = df.append(pd.read_csv(csv))
        return df

    def upload_df(self, df: pd.DataFrame) -> None:
        raise RuntimeError('Not implemented')

    def load(self) -> None:
        self.upload_df(self.load_df())


class TermsLoader(ZipFileLoader):

    def __init__(self, zip_file: ZipFile = None, files: list = None):
        from apps.deployment.app_vars import DEPLOYMENT_TERMS_INITIALIZED
        super().__init__(zip_file, files, DEPLOYMENT_TERMS_INITIALIZED)

    def upload_df(self, df: pd.DataFrame) -> None:
        if Term.objects.exists():
            print('Terms data already uploaded')
            return
        print('Uploading terms...')

        with transaction.atomic():
            terms_count = load_terms(df)

        print('Detected %d terms' % terms_count)
        print('Caching terms config for Locate tasks...')

        dict_data_cache.cache_term_stems()


class CourtsLoader(ZipFileLoader):

    def __init__(self, zip_file: ZipFile = None, files: list = None):
        from apps.deployment.app_vars import DEPLOYMENT_COURTS_INITIALIZED
        super().__init__(zip_file, files, DEPLOYMENT_COURTS_INITIALIZED)

    def upload_df(self, df: pd.DataFrame) -> None:
        if Court.objects.exists():
            print('Courts data already uploaded')
            return
        print('Uploading courts...')

        with transaction.atomic():
            courts_count = load_courts(df)

        print('Detected %d courts' % courts_count)
        print('Caching courts config for Locate tasks...')

        dict_data_cache.cache_court_config()


class GeoEntitiesLoader(ZipFileLoader):

    def __init__(self, zip_file: ZipFile = None, files: list = None):
        from apps.deployment.app_vars import DEPLOYMENT_GEOENTITIES_INITIALIZED
        super().__init__(zip_file, files, DEPLOYMENT_GEOENTITIES_INITIALIZED)

    def upload_df(self, df: pd.DataFrame) -> None:
        if GeoEntity.objects.exists():
            print('Geo config data already uploaded')
            return
        print('Uploading geo config...')

        with transaction.atomic():
            geo_aliases_count, geo_entities_count = load_geo_entities(df)

        print('Total created: %d GeoAliases' % geo_aliases_count)
        print('Total created: %d GeoEntities' % geo_entities_count)
        print('Caching geo config for Locate tasks...')

        dict_data_cache.cache_geo_config()


class DictionaryLoader(DataLoader):

    dictionary_loader_by_file_prefix = dict(
        terms=TermsLoader,
        courts=CourtsLoader,
        geoentities=GeoEntitiesLoader
    )

    def __init__(self, file_patch: str):
        super().__init__()
        self.file_patch = file_patch

    def load(self) -> None:
        zip_file = ZipFile(self.file_patch)
        files_by_loader = dict()
        for file_info in zip_file.infolist():
            if file_info.filename.endswith('/'):
                continue
            for prefix, LoaderClass in DictionaryLoader.dictionary_loader_by_file_prefix.items():
                if file_info.filename.startswith(prefix):
                    files = files_by_loader.get(LoaderClass)
                    if not files:
                        files = list()
                        files_by_loader[LoaderClass] = files
                    files.append(file_info)
                    break
        for LoaderClass, files in files_by_loader.items():
            loader = LoaderClass(zip_file=zip_file, files=files)
            loader.load_once()


class DocumentDataLoader(DataLoader):

    def __init__(self, file_patch: str):
        from apps.deployment.app_vars import DEPLOYMENT_DOCUMENT_DATA_INITIALIZED
        super().__init__(DEPLOYMENT_DOCUMENT_DATA_INITIALIZED)
        self.file_patch = file_patch

    def load(self) -> None:
        initialized = False
        for document_type in DocumentType.objects.all()[:2]:
            if document_type.code != 'document.GenericDocument':
                initialized = True
                break
        initialized = initialized or DocumentField.objects.exists()
        if initialized:
            print('Document data already uploaded')
            return
        print('Uploading document data...')

        zip_file = ZipFile(self.file_patch)
        for file_info in zip_file.infolist():
            data = zip_file.read(file_info)
            buf = io.StringIO()
            with NamedTemporaryFile(mode='wb', suffix='.json') as tmp_file:
                tmp_file.write(data)
                tmp_file.seek(0)
                call_command('loaddata', tmp_file.name, app_label='document', stdout=buf)
                buf.seek(0)
        DocumentField.objects.update(dirty=False, training_finished=False)


class TermsByUrlLoader(TermsLoader):

    def __init__(self):
        super().__init__()

    def load_df(self) -> pd.DataFrame:
        return load_df(get_terms_data_urls())


class CourtsByUrlLoader(CourtsLoader):

    def __init__(self):
        super().__init__()

    def load_df(self) -> pd.DataFrame:
        return load_df(get_courts_data_urls())


class GeoEntitiesByUrlLoader(GeoEntitiesLoader):

    def __init__(self):
        super().__init__()

    def load_df(self) -> pd.DataFrame:
        return load_df(get_geoentities_data_urls())


class Command(BaseCommand):
    help = 'Uploads application data from specified folder'

    loader_by_file_prefix = dict(
        document_data=lambda file_patch: DocumentDataLoader(file_patch).load_once(),
        dict_data=lambda file_patch: DictionaryLoader(file_patch).load_once()
    )

    def get_file_loader(self, file: str) -> Optional[Callable[[str], None]]:
        for prefix, loader in self.loader_by_file_prefix.items():
            if file.startswith(str(prefix)):
                return loader
        return None

    def add_arguments(self, parser) -> None:
        parser.add_argument('--data-dir', required=False, type=str)
        parser.add_argument('--upload-dict-data-from-repository', default=False, action='store_true')
        parser.add_argument('--arch-files',  default=False, action='store_true')

    @classmethod
    def get_proceed_dir(cls, data_dir):
        proceed_dir = '{0}/processed/{1}'.format(data_dir, now().strftime('%Y-%m-%d_%H-%M-%S'))
        if not path.exists(proceed_dir):
            pathlib.Path(proceed_dir).parent.mkdir(parents=True, exist_ok=True)
            mkdir(proceed_dir)
        return proceed_dir

    def handle(self, *args: Tuple, **options: Dict[Any, Any]) -> None:
        data_dir = options.get('data_dir')
        upload_dict_data_from_repository = options.get('upload_dict_data_from_repository')
        arch_files = options.get('arch_files')

        if data_dir:
            print('Uploading application data from {0}...'.format(data_dir))
            if path.exists(data_dir):
                for file in listdir(data_dir):
                    if not path.isdir(file) and file.endswith('.zip'):
                        print('Processing {0}...'.format(file))
                        file_patch = '{0}/{1}'.format(data_dir, file)
                        loader = self.get_file_loader(file)
                        if loader:
                            loader(file_patch)
                        if arch_files:
                            shutil.move(file_patch, '{0}/{1}'.format(self.get_proceed_dir(data_dir), file))
            else:
                print('Data folder does not exist')

        if upload_dict_data_from_repository:
            print('Uploading dictionary data data from repository...'.format(data_dir))
            TermsByUrlLoader().load_once()
            CourtsByUrlLoader().load_once()
            GeoEntitiesByUrlLoader().load_once()
