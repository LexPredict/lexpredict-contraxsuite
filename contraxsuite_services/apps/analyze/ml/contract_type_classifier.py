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
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# standard library
import json
import tarfile
import inspect
from pathlib import Path
from zipfile import ZipFile
from io import BufferedReader
from datetime import datetime
from dataclasses import dataclass
from contextlib import contextmanager
from tempfile import TemporaryDirectory
from typing import Any, Callable, Dict, Final, Generator, Iterable, Optional, Tuple, Union

# third-party imports
import magic
import cloudpickle
from pandas import Series
from cachetools import LRUCache
from sklearn.pipeline import Pipeline

# LexNLP
from lexnlp.extract.en.contracts.predictors import ProbabilityPredictorContractType

# ContraxSuite
from apps.common.log_utils import ProcessLogger
from apps.common.file_storage import get_file_storage, ContraxsuiteFileStorage


@contextmanager
def _return_buffered_reader(
    buffered_reader: BufferedReader,
) -> Generator[BufferedReader, None, None]:
    """
    """
    try:
        yield buffered_reader
    finally:
        pass


MIME_TO_ARCHIVE_OPENING_FUNCTION: Final[Dict[str, Callable]] = {
    # compressed tar files
    # https://docs.python.org/3.8/library/tarfile.html
    'application/x-bzip2': lambda f, m: tarfile.open(fileobj=f, mode=f'r{m}bz2'),
    'application/x-xz': lambda f, m: tarfile.open(fileobj=f, mode=f'r{m}xz'),
    'application/gzip': lambda f, m: tarfile.open(fileobj=f, mode=f'r{m}gz'),

    # unsure whether to use mode='r|' or mode='r|*'
    # https://docs.python.org/3.8/library/tarfile.html
    'application/x-tar': lambda f, m: tarfile.open(fileobj=f, mode=f'r{m}'),

    # lucky for us, ZipFile's API is very similar to TarFile
    # https://docs.python.org/3.8/library/zipfile.html
    'application/zip': lambda f, m: ZipFile(file=f, mode='r'),

    # not an archive
    'application/octet-stream': lambda f, m: _return_buffered_reader(f),
}


@dataclass(eq=False)
class FileInformation:
    """
    Used to track whether a given file has changed.
    """
    path: str
    last_modified: datetime
    size_bytes: int

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return (
            self.path == other.path
            and self.last_modified == other.last_modified
            and self.size_bytes == other.size_bytes
        )


class ContractTypeClassifier:
    """
    This class wraps functionality defined by ProbabilityPredictorContractType.
    The ContractTypeClassifier class builds instances of ProbabilityPredictorContractType
    with current models taken from ContraxSuiteFileStorage (WebDAV or local filesystem).

    Double-caching system:

        This class maintains two least-recently used caches (size=3):

        - cls._cache_files
        - cls._cache_probability_predictor_contract_type

        `cls._cache_probability_predictor_contract_type` stores instances of the
        ProbabilityPredictorContractType class. It is keyed using a tuple of
        (str, int), with the first value representing a language and the second
        value representing a project ID. The default is ("en", 0).

        `cls._cache_files` keeps track of the current state of a file associated with a key.
        It is keyed in the same way as `cls._cache_probability_predictor_contract_type`.

        `cls._cache_files` is required because the underlying model files used
        by instances of ProbabilityPredictorContractType might change
        (i.e.: re-uploaded with a different version) within the lifetime of a
        loaded ContractTypeClassifier.
    """
    pipeline_file_name: Optional[str] = None
    pipeline_file_member: Optional[str] = None
    fallback_to_lexnlp_default_pipeline: bool = True
    unknown_classification: str = 'UNKNOWN'

    _file_storage: Optional[ContraxsuiteFileStorage] = None

    # key: Tuple[str, int], value: FileInformation
    _cache_files: LRUCache = LRUCache(3)

    # key: Tuple[str, int], value: ProbabilityPredictorContractType
    _cache_probability_predictor_contract_type: LRUCache = LRUCache(3)

    def __new__(cls, *args, **kwargs):
        raise RuntimeError(f'{cls} should not be instantiated')

    @classmethod
    def predict_classifications(
        cls,
        log: ProcessLogger,
        document_sentences: Iterable[str],
        document_language: str = '',
        project_id: int = 0,
    ) -> Tuple[str, Tuple[Tuple[str, float]]]:
        """
        Args:
            log (ProcessLogger):
                Logger from the root task from which this method is called.

            document_sentences (Iterable[str]):
                TextUnit sentences of a document which should be classified as
                a type of contract. These sentences should be in order of
                appearance in the source document.

            document_language (str=''):
                Specifies the language of the contract classification model.
                Used as the first half of the cache key.

            project_id (int=0):
                Specifies the project ID of the contract classification model.
                Used as the second half for the cache key.

        Returns:
            A tuple containing an inferred contract type classification as its first element
            and a tuple of two-element tuples with prediction-probability pairs as its second element.
        """
        from apps.document.app_vars import DETECT_CONTRACT_TYPE_SETTINGS
        filter_json = DETECT_CONTRACT_TYPE_SETTINGS.val(project_id=project_id)
        try:
            if filter_json:
                loaded_filter_json = json.loads(filter_json)
                cls.pipeline_file_name = loaded_filter_json.get('pipeline_file_name')
                cls.pipeline_file_member = loaded_filter_json.get('pipeline_file_member')
                cls.fallback_to_lexnlp_default_pipeline = \
                    loaded_filter_json.get('fallback_to_lexnlp_default_pipeline', True)

            else:
                raise Exception(f'Could not load a DETECT_CONTRACT_TYPE_SETTINGS AppVar value from {project_id=}')

        except Exception as exception:
            message: str = \
                f"{DETECT_CONTRACT_TYPE_SETTINGS.name} AppVar value ({filter_json}) " \
                f"is not formatted correctly. See the variable's default value."
            log.error(
                message=message,
                exc_info=exception,
            )
            value_error = ValueError(message)
            raise value_error from exception

        probability_predictor_contract_type: ProbabilityPredictorContractType = \
            cls.get_probability_predictor_contract_type(
                log=log,
                document_language=document_language,
                project_id=project_id,
                fallback_to_lexnlp_default_pipeline=cls.fallback_to_lexnlp_default_pipeline,
            )

        predictions: Series = probability_predictor_contract_type.make_predictions(
            text=document_sentences,
            top_n=5,
        )

        signature: inspect.Signature = inspect.signature(obj=probability_predictor_contract_type.infer_classification)
        default_arguments: Dict[str, Any] = {
            parameter: argument.default
            for parameter, argument in signature.parameters.items()
            if argument.default is not inspect.Parameter.empty
        }
        kwargs_for_infer_classification: Dict[str, Any] = {
            parameter: loaded_filter_json.get(parameter) or getattr(cls, parameter) or argument
            for parameter, argument in default_arguments.items()
        }

        log.debug(
            f'Running `probability_predictor_contract_type.infer_classification()`'
            f' with arguments: {kwargs_for_infer_classification}'
        )
        contract_classification: str = probability_predictor_contract_type.infer_classification(
            predictions=predictions,
            **kwargs_for_infer_classification,
        )

        # noinspection PyTypeChecker
        return contract_classification, tuple(predictions.items())

    @classmethod
    def _update_file_cache(
        cls,
        log: ProcessLogger,
        document_language: str,
        project_id: int,
    ) -> None:
        """
        Updates `cls._cache_files[key]` if the tracked file has changed and if
        necessary, invalidates `cls._cache_probability_predictor_contract_type[key]`.

        Args:

            log (ProcessLogger):
                Logger from the root task from which this method is called.

            document_language (str=''):
                Specifies the language of the contract classification model.
                Used as the first half of the cache key.

            project_id (int=0):
                Specifies the project ID of the contract classification model.
                Used as the second half for the cache key.

        Returns:
            None
        """

        # UNUSED: algorithm to search for model files
        # def _find_file(_document_language: str, _project_id: int) -> str:
        #     keys = [(_document_language, _project_id)]
        #     if _document_language != cls.DEFAULT_LANGUAGE:
        #         keys.append((cls.DEFAULT_LANGUAGE, _project_id))
        #         if _project_id:
        #             keys.append((cls.DEFAULT_LANGUAGE, 0))
        #     elif _project_id:
        #         keys.append((_document_language, 0))
        #
        #     for doc_lang, proj_id in keys:
        #         _directory = cls._get_model_folder(doc_lang, proj_id)
        #         _file_names: list = file_storage.list(directory)
        #         _path: Optional[str] = None
        #         for _file_name in _file_names:
        #             if cls.pipeline_file_name in _file_name:
        #                 _path = _file_name
        #         if _path:
        #             return _path

        key: Tuple[str, int] = (document_language, project_id)
        file_storage: ContraxsuiteFileStorage = cls._get_file_storage()
        file_information_cached: Optional[FileInformation] = cls._cache_files.get(key)

        if file_information_cached is None:
            directory: str = cls._get_model_folder(document_language, project_id)
            file_names: list = file_storage.list(directory)
            if not file_names:
                directory: str = cls._get_model_folder(document_language, 0)
                file_names: list = file_storage.list(directory)
            path: Optional[str] = None
            for file_name in file_names:
                if cls.pipeline_file_name and file_name.endswith(cls.pipeline_file_name):
                    path = file_name

            if path is None:
                raise RuntimeError(
                    f'Could not load a contract type classification'
                    f' pipeline file for ({document_language=}, {project_id=}).'
                )

            file_info: Dict[str, Union[datetime, int]] = file_storage.file_info(path)
            cls._cache_files[key] = FileInformation(
                path=path,
                last_modified=file_info['date'],
                size_bytes=file_info['size'],
            )
            return
        file_info: Dict[str, Union[datetime, int]] = file_storage.file_info(file_information_cached.path)
        file_information_current: FileInformation = FileInformation(
            path=file_information_cached.path,
            last_modified=file_info['date'],
            size_bytes=file_info['size'],
        )
        if file_information_cached != file_information_current:
            log.debug('FileInformation mismatch; updating caches.')
            cls._cache_files[key] = file_information_current
            cls._cache_probability_predictor_contract_type[key] = None
            return

    @classmethod
    def _get_model_folder(cls, language: str, project_id: int) -> str:
        """
        Retrieves a string representing a relative path within ContraxSuiteFileStorage;
        models for (language, project_id) are stored within that directory.

        Args:
            language (str):
                Specifies the language of the contract classification model.
                Used as the first half of the cache key.

            project_id (int):
                Specifies the project ID of the contract classification model.
                Used as the second half for the cache key.

        Returns:
            A string representing a relative path within ContraxSuiteFileStorage.
        """
        # TODO: why 'document' instead of 'project'?
        path = f'models/{language or "en"}/contract_type_classifier/document'
        if project_id:
            path += f"/{project_id}"
        return path

    @classmethod
    def _get_file_storage(cls) -> ContraxsuiteFileStorage:
        """
        Useful for testing; cls._file_storage can be set to a TestFileStorage object.
        """
        if not cls._file_storage:
            cls._file_storage = get_file_storage()
        return cls._file_storage

    @classmethod
    def _load_pipeline(cls, key: Tuple[str, int]) -> Pipeline:
        """
        Attempts to load and return a pickled Scikit-Learn Pipeline from
        ContraxSuiteFileStorage.

        Steps:
            1. Get the ContraxSuiteFileStorage file locally as a temporary file
            2. Open the temporary file and infer its MIME type.
            3. Based on the MIME type, get and use the correct opening function
                ... (for .zip, .tar, .tar.gz, .tar.xz, no extension).
            4. If the opened file is not an archive, attempt to unpickle the Pipeline.
            5. If cls.pipeline_file_member was defined by the AppVar, extract it.
                ... otherwise, take the first popped file from the archive.
            6. Then, try to unpickle the Pipeline.

        Args:
            key (Tuple[str, int):
                A tuple of (document_language, project_id); used as a cache key.

        Returns:
            A Scikit-Learn Pipeline loaded from a pickle.
        """

        def _unpickle_pipeline(pickled, **details) -> Pipeline:
            try:
                return cloudpickle.load(pickled)
            except Exception as exception:
                raise Exception(
                    f'Could not unpickle {pickled} using cloudpickle. '
                    f'Details: {details}'
                ) from exception

        file_information: FileInformation = cls._cache_files.get(key)
        file_storage: ContraxsuiteFileStorage = cls._get_file_storage()
        with file_storage.get_as_local_fn(file_information.path) as (path_local_temp, _):
            path_local_temp: Path = Path(path_local_temp)
            with open(path_local_temp, 'rb') as buffer:
                mime: str = magic.from_buffer(buffer=buffer.read(1024), mime=True)
                buffer.seek(0)
                opening_function: Callable = MIME_TO_ARCHIVE_OPENING_FUNCTION[mime]
                with opening_function(
                    buffer,
                    ':' if cls.pipeline_file_member else '|',
                ) as opened:
                    if isinstance(opened, BufferedReader):
                        return _unpickle_pipeline(
                            pickled=opened,
                            file_information_path=file_information.path,
                            mime=mime,
                            type_opened=type(opened),
                            pipeline_file_name=cls.pipeline_file_name,
                            pipeline_file_member=cls.pipeline_file_member,
                        )
                    elif isinstance(opened, (tarfile.TarFile, ZipFile)):
                        with TemporaryDirectory() as temporary_directory:
                            path_temporary_directory: Path = Path(temporary_directory)
                            if cls.pipeline_file_member:
                                opened.extract(
                                    member=cls.pipeline_file_member,
                                    path=path_temporary_directory,
                                )
                                path_pipeline: Path = path_temporary_directory / cls.pipeline_file_member
                            else:
                                opened.extractall(path=path_temporary_directory)
                                path_pipeline: Path = next(
                                    p for p in path_temporary_directory.rglob('*')
                                    if p.is_file()
                                )
                            with path_pipeline.open('rb') as f:
                                return _unpickle_pipeline(
                                    pickled=f,
                                    file_information_path=file_information.path,
                                    mime=mime,
                                    type_opened=type(opened),
                                    pipeline_file_name=cls.pipeline_file_name,
                                    pipeline_file_member=cls.pipeline_file_member,
                                )
                    else:
                        raise TypeError(
                            f'Cannot handle opened file: {opened}. '
                            f'Expected: TarFile, ZipFile, or BufferedReader. '
                            f'Received: {type(opened)}. '
                            f'MIME type: {mime}. '
                            f'File: {file_information.path}. '
                            f'{cls.pipeline_file_name=} '
                            f'{cls.pipeline_file_member=}'
                        )

    @classmethod
    def get_probability_predictor_contract_type(
        cls,
        log: ProcessLogger,
        document_language: str,
        project_id: int,
        fallback_to_lexnlp_default_pipeline: bool = True,
    ) -> ProbabilityPredictorContractType:
        """
        Fetches the correct ProbabilityPredictorContractType from the cache or
        instantiates a caches a new ProbabilityPredictorContractType if one
        could not be found under the key (document_language, project_id).

        Args:
            log (ProcessLogger):
                Logger from the root task from which this method is called.

            document_language (str)
                Specifies the language of the contract classification model.
                Used as the first half of the cache key.

            project_id (int):
                Specifies the project ID of the contract classification model.
                Used as the second half for the cache key.

            fallback_to_lexnlp_default_pipeline (bool=True):
                Whether to use LexNLP's default contract type classification
                pipeline if no local pipeline can be loaded.

        Returns:
            An instantiated ProbabilityPredictorContractType.
        """
        key: Tuple[str, int] = (document_language, project_id)

        try:
            cls._update_file_cache(
                log=log,
                document_language=document_language,
                project_id=project_id,
            )
        except RuntimeError as runtime_error:
            if fallback_to_lexnlp_default_pipeline:
                exception_message: str = \
                    f'Could not load a contract type classification' \
                    f' pipeline file for ({document_language=}, {project_id=}).'
                try:
                    # noinspection PyProtectedMember
                    log.error(
                        f'{exception_message}'
                        f' Attempting to load {ProbabilityPredictorContractType._DEFAULT_PIPELINE=}...'
                    )

                    probability_predictor_contract_type: ProbabilityPredictorContractType = \
                        ProbabilityPredictorContractType()

                    # noinspection PyProtectedMember
                    log.info(
                        f'Using {ProbabilityPredictorContractType._DEFAULT_PIPELINE=}'
                        f' as a contract type classification pipeline for ({document_language=}, {project_id=}).'
                    )

                    cls._cache_probability_predictor_contract_type[key] = probability_predictor_contract_type
                    return probability_predictor_contract_type

                except FileNotFoundError as file_not_found_error:
                    raise RuntimeError(exception_message) from file_not_found_error
            else:
                raise runtime_error

        probability_predictor_contract_type: ProbabilityPredictorContractType = \
            cls._cache_probability_predictor_contract_type.get(key)
        if probability_predictor_contract_type is None:
            pipeline: Pipeline = cls._load_pipeline(key)
            probability_predictor_contract_type: ProbabilityPredictorContractType = \
                ProbabilityPredictorContractType(pipeline=pipeline)
            log.debug(f'Caching: {probability_predictor_contract_type}')
            cls._cache_probability_predictor_contract_type[key] = probability_predictor_contract_type
        else:
            log.debug(
                f'Retrieved from cache_probability_predictor_contract_type: '
                f'{probability_predictor_contract_type}'
            )
        return probability_predictor_contract_type
