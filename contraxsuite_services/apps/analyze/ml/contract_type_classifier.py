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


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import json
import os
import datetime
import shutil
import tempfile
import zipfile
from typing import List, Optional, Dict, Tuple

from lexnlp.extract.en.contracts.contract_type_detector import ContractTypeDetector

from apps.common.file_storage import get_file_storage, ContraxsuiteFileStorage


class ModelFileInfo:
    def __init__(self,
                 full_path: str,
                 name_only: str,
                 is_zip: bool,
                 size: int,
                 modified: datetime.datetime):
        self.full_path = full_path
        self.name_only = name_only
        self.is_zip = is_zip
        self.size = size
        self.modified = modified

    def __str__(self):
        s_zip = ', zip' if self.is_zip else ''
        return f'{self.full_path}{s_zip}, {self.size} bytes, modified: {self.modified}'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.full_path == other.full_path and self.is_zip == other.is_zip \
            and self.size == other.size and self.modified == other.modified


class ContractTypeClassifier:
    """
    The class wraps ContractTypeDetector class.
    The ContractTypeClassifier class provides the ContractTypeDetector
    with actual models taken from WebDAV storage.
    """

    RF_MODEL_FILE = 'rf_model'
    D2V_MODEL_FILE = 'd2v_model'

    UNKNOWN_CONTRACT_TYPE = 'UNKNOWN'

    DEFAULT_LANGUAGE = 'en'

    file_storage: Optional[ContraxsuiteFileStorage] = None

    cached_model_files: Dict[str, ModelFileInfo] = {}

    # key: (language, project_id)
    # value:
    cached_contract_detector: Dict[Tuple[str, int], ContractTypeDetector] = {}

    @classmethod
    def get_document_contract_type(cls,
                                   document_text: str,
                                   dont_check_for_new_model: bool = False,
                                   document_language: str = '',
                                   project_id: int = 0) -> Tuple[str, List[Tuple[str, float]]]:
        """
        :param document_text: document plain text
        :param dont_check_for_new_model: should the method check for updated detector files in WebDAV
        :param document_language: language is the key for the specific model
        :param project_id: project_id can also be a key for the specific model
        :return: (contract type), ([(contract type: prob], ... [...])
        """
        document_language = document_language or cls.DEFAULT_LANGUAGE

        from apps.document.app_vars import CONTRACT_TYPE_FILTER
        filter_json = CONTRACT_TYPE_FILTER.val()
        min_prob = 0.0
        max_closest_percent = 100
        try:
            if filter_json:
                filter = json.loads(filter_json)
                min_prob = filter['min_prob']
                max_closest_percent = filter['max_closest_percent']
        except:
            raise Exception(f'{CONTRACT_TYPE_FILTER.name} var value ({filter_json}) has incorrect format, ' +
                            "see the variable's default value")

        detector = cls.cached_contract_detector.get((document_language, project_id))
        if not dont_check_for_new_model or not detector:
            detector = cls.get_contract_detector(document_language, project_id)
        v = detector.detect_contract_type_vector(document_text)
        c_type = detector.detect_contract_type(v, min_prob, max_closest_percent)
        return c_type or cls.UNKNOWN_CONTRACT_TYPE, list(v.items())

    @classmethod
    def get_contract_detector(cls,
                              document_language: str,
                              project_id: int) -> ContractTypeDetector:
        # check the model files are the same since they were cached
        # first we try specified language and project id,
        # then we try the same language w/o project ID,
        # finally we try default language
        keys = [(document_language, project_id)]
        if document_language != cls.DEFAULT_LANGUAGE:
            keys.append((cls.DEFAULT_LANGUAGE, project_id))
            if project_id:
                keys.append((cls.DEFAULT_LANGUAGE, 0))
        elif project_id:
            keys.append((document_language, 0))

        for language, proj_id in keys:
            is_default_key = language == cls.DEFAULT_LANGUAGE and not proj_id
            file_infos = cls.get_model_file_infos(language, proj_id, is_default_key)
            if not file_infos:
                continue
            if document_language != language or project_id != proj_id:
                print(f'get_contract_detector(lang={document_language}, proj={project_id}): used ' +
                      f'(lang={language}, proj={proj_id}) instead')
            if cls.is_cache_actual(file_infos):
                return cls.cached_contract_detector[(language, proj_id)]
            return cls.build_and_cache_model(file_infos, language, proj_id)
        raise Exception('ContractTypeClassifier: no model files are found')

    @classmethod
    def build_and_cache_model(cls,
                              file_infos: Dict[str, ModelFileInfo],
                              document_language: str,
                              project_id: int) -> ContractTypeDetector:
        # download files from storage into temporary path, unpack if needed
        # then build the model and update the cache
        fstor = cls.get_file_storage()

        with fstor.get_as_local_fn(file_infos[cls.RF_MODEL_FILE].full_path) as (fn_rf, _uri):
            with fstor.get_as_local_fn(file_infos[cls.D2V_MODEL_FILE].full_path) as (fn_dv, _uri):
                temp_dir = tempfile.mkdtemp()
                try:
                    rf_final_path = cls.get_path_to_unpacked_file(
                        file_infos[cls.RF_MODEL_FILE], fn_rf, temp_dir)
                    dv_final_path = cls.get_path_to_unpacked_file(
                        file_infos[cls.D2V_MODEL_FILE], fn_dv, temp_dir)

                    detector = ContractTypeDetector(
                        rf_final_path,
                        dv_final_path)
                finally:
                    shutil.rmtree(temp_dir)

                cls.cached_contract_detector[(document_language, project_id)] = detector
                cls.cached_model_files = file_infos
                return detector

    @classmethod
    def get_path_to_unpacked_file(
            cls, file_info: ModelFileInfo, local_path: str, dest_folder: str) -> str:
        if not file_info.is_zip:
            return local_path
        # unpack into temporary folder
        tmp_file_folder = os.path.join(dest_folder, file_info.name_only)
        with zipfile.ZipFile(local_path, 'r') as zip_ref:
            zip_ref.extractall(tmp_file_folder)
        # get path to the only file in the folder
        for f in os.listdir(tmp_file_folder):
            return os.path.join(tmp_file_folder, f)

    @classmethod
    def is_cache_actual(cls, file_infos: Dict[str, ModelFileInfo]) -> bool:
        if not cls.cached_contract_detector:
            return False
        for file_name in file_infos:
            if file_name not in cls.cached_model_files:
                return False
            if file_infos[file_name] != cls.cached_model_files[file_name]:
                return False
        return True

    @classmethod
    def get_model_file_infos(cls,
                             document_language: str,
                             project_id: int,
                             raise_exception: bool = True) -> Dict[str, ModelFileInfo]:
        path = cls.get_model_folder(document_language, project_id)
        file_names = cls.get_file_storage().list(path)
        rf_inf = cls.find_model_file(cls.RF_MODEL_FILE, file_names)
        if not rf_inf:
            if raise_exception:
                raise Exception(f'File {cls.RF_MODEL_FILE} was not found in {path} storage path')
            return {}
        dv_inf = cls.find_model_file(cls.D2V_MODEL_FILE, file_names)
        if not dv_inf:
            if raise_exception:
                raise Exception(f'File {cls.D2V_MODEL_FILE} was not found in {path} storage path')
            return {}
        return {cls.RF_MODEL_FILE: rf_inf, cls.D2V_MODEL_FILE: dv_inf}

    @classmethod
    def find_model_file(cls,
                        name_only: str,
                        files: List[str]) -> Optional[ModelFileInfo]:
        file_datas: List[ModelFileInfo] = []
        f_stor = cls.get_file_storage()
        for file_path in files:
            file_name = os.path.basename(file_path)
            file_name, extension = os.path.splitext(file_name)
            if file_name != name_only:
                continue
            fi = f_stor.file_info(file_path)
            file_datas.append(ModelFileInfo(
                file_path,
                file_name,
                is_zip=extension.lower() == '.zip',
                size=fi['size'],
                modified=fi['date']
            ))
        # return the latest record
        if not file_datas:
            return None
        file_datas.sort(key=lambda f: f.modified, reverse=True)
        return file_datas[0]

    @classmethod
    def get_file_storage(cls) -> ContraxsuiteFileStorage:
        if not cls.file_storage:
            cls.file_storage = get_file_storage()
        return cls.file_storage

    @classmethod
    def get_model_folder(cls, language: str, project_id: int) -> str:
        path = f'models/{language or "en"}/contract_type_classifier/document'
        if project_id:
            path += f'/{project_id}'
        return path
