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

import inspect
import os
import time
from shutil import rmtree
from subprocess import Popen
from tempfile import gettempdir
from tempfile import mkdtemp
from threading import RLock
from threading import Thread
from typing import Dict, List
from uuid import uuid4

from apps.common.logger import CsLogger
from apps.common.singleton import Singleton

import mlflow.pyfunc as pyfunc
from dataclasses import dataclass
from django.conf import settings
from mlflow.pyfunc import Model
from mlflow.tracking.artifact_utils import _download_artifact_from_uri

from apps.common.processes import start_process
from apps.mlflow import mlflow_socket_server_script
from apps.mlflow.mlflow_model_client import predict_on_server

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


MLFLOW_S3_ENDPOINT_URL = 'MLFLOW_S3_ENDPOINT_URL'

AWS_SECRET_ACCESS_KEY = 'AWS_SECRET_ACCESS_KEY'

AWS_ACCESS_KEY_ID = 'AWS_ACCESS_KEY_ID'

logger = CsLogger.get_logger(settings.MLFLOW_LOGGER_NAME)


@dataclass
class ModelInfo:
    model_uri: str
    model_dir: str
    process: Popen
    unix_socket_path: str
    last_used_time: float


@Singleton
class MLFlowModelManager:
    """
    Manages loading MLFLow models, starting their socket servers within the Contraxsuite virtual env,
    killing their processes and unloading the models.


    Work scheme:

    When a prediction is requested with a model uri the instance of this class:
        - checks if model is loaded and loads if needed;
        - connects to the model socket server, sends model input, receives model output.

    Model loading procedure:
        - download the model artifact into a temp dir;
        - copy socket server script into the model folder (mlflow_socket_server_script.py);
        - reserve a temp file name for using as unix file socket path;
        - start the socket server in the model dir specifying it to bind at the reserved file socket;
        - if not already started - start a watcher thread which cleanups the unused models.

    Watcher thread periodically checks the loaded models and un-loads those which are not used (predict) for too long.

    Model un-loading procedure:
        - kill model process;
        - remove model directory.


    So models are loaded on first predict request and are unloaded after they are not used for the specified amount
    of time.
    Each model is started in its own process. This is done to avoid loading the models' python code into the main
    process which can cause naming conflicts and other problems.


    """

    def __init__(self) -> None:
        super().__init__()
        self.lock = RLock()
        self.models = {}  # type: Dict[str, ModelInfo]
        self.thread = None
        self.started = False
        self.predict_timeout = None
        self.server_init_timeout = None
        self.server_idle_timeout = None
        self.last_cleanup_time = time.time()
        self._update_app_vars()
        self.apply_os_env_from_settings()
        self.watch_thread = None

    def _watch(self):
        while True:
            self.lock.acquire()
            try:
                self._cleanup()
                if not self.models:
                    self.watch_thread = None
                    logger.info('No more MLFlow models loaded. Stopping watcher thread.')
                    return
            finally:
                self.lock.release()
            time.sleep(20)

    def _ensure_watcher_running(self):
        self.lock.acquire()
        try:
            if not self.watch_thread and self.models:
                logger.info('Starting a thread to watch and cleanup MLFlow models...')
                self.watch_thread = Thread(target=self._watch, daemon=True)
                self.watch_thread.start()
        finally:
            self.lock.release()

    def apply_os_env_from_settings(self):
        os.environ[AWS_ACCESS_KEY_ID] = settings.AWS_ACCESS_KEY_ID
        os.environ[AWS_SECRET_ACCESS_KEY] = settings.AWS_SECRET_ACCESS_KEY
        os.environ[MLFLOW_S3_ENDPOINT_URL] = settings.MLFLOW_S3_ENDPOINT_URL

    def _update_app_vars(self):
        from apps.mlflow.app_vars import MLFLOW_MODEL_SERVER_STARTUP_TIMEOUT_SEC, MLFLOW_PREDICT_TIMEOUT_SEC, \
            MLFLOW_MODEL_SERVER_IDLE_TIMEOUT_SEC
        self.predict_timeout = MLFLOW_PREDICT_TIMEOUT_SEC.val()
        self.server_init_timeout = MLFLOW_MODEL_SERVER_STARTUP_TIMEOUT_SEC.val()
        self.server_idle_timeout = MLFLOW_MODEL_SERVER_IDLE_TIMEOUT_SEC.val()

    def _init_model(self, model_uri: str):
        self.lock.acquire()
        try:
            temp_dir = mkdtemp()
            local_path = _download_artifact_from_uri(model_uri, output_path=temp_dir)

            # copy server script into model dir
            server_script_name = mlflow_socket_server_script.__name__.split('.')[-1] + '.py'
            src = inspect.getsource(mlflow_socket_server_script)
            with open(os.path.join(local_path, server_script_name), 'w') as f:
                f.write(src)

            model = Model.load(local_path)

            pyfunc_flavor_config = model.flavors.get(pyfunc.FLAVOR_NAME)

            if not pyfunc_flavor_config:
                raise RuntimeError(f'Only python function mlflow models are supported.\n'
                                   f'Model has no python function flavor: {model_uri}\n'
                                   f'Model flavors are:\n{sorted(model.flavors.keys())}')

            if os.name == "nt":
                raise RuntimeError(f'Only unix-like OS are supported for running mlflow servers.\n'
                                   f'Running on os: {os.name}')

            unix_socket_path = os.path.join(gettempdir(), str(uuid4()))

            def log_info(s: str):
                logger.info(f'MLFlow model server {model_uri}: {s}')

            def log_error(s: str):
                logger.error(f'MLFlow model server {model_uri}: {s}')

            # Run the simple socket server in the background.
            ps = start_process(['python', server_script_name, model_uri, unix_socket_path],
                               cwd=local_path,
                               stdout=log_info, stderr=log_error)

            if not os.path.exists(unix_socket_path):
                start = time.time()
                while True:
                    if os.path.exists(unix_socket_path):
                        break
                    if time.time() - start > self.server_init_timeout:
                        raise TimeoutError(f'Timeout waiting for model process startup: {model_uri}')
                    time.sleep(0.5)

            self.models[model_uri] = ModelInfo(model_uri=model_uri,
                                               model_dir=temp_dir,
                                               unix_socket_path=unix_socket_path,
                                               last_used_time=time.time(),
                                               process=ps)
            logger.info(f'Loaded model: {model_uri}\n'
                        f'local path: {local_path}')
        except Exception as e:
            logger.error(f'Unable to load model: {model_uri}', exc_info=e)
        finally:
            self.lock.release()

    def _remove_model(self, model_uri: str):
        self.lock.acquire()
        try:
            if model_uri not in self.models:
                logger.info(f'Model is not registered: {model_uri}')
                return
            model_info = self.models[model_uri]

            try:
                if model_info.process.poll() is None:
                    model_info.process.kill()
                    model_info.process.wait(20)
            except Exception as e:
                logger.error(f'Unable to kill process of model: {model_uri}\n'
                             f'Will still try to delete its local dir.', exc_info=e)

            try:
                rmtree(model_info.model_dir)
            except Exception as e:
                logger.error(f'Unable to delete local dir of model: {model_uri}\n'
                             f'Dir: {model_info.model_dir}', exc_info=e)
            del self.models[model_uri]
        finally:
            self.lock.release()

    def _cleanup(self):
        self._update_app_vars()
        self.lock.acquire()
        try:
            for model_uri in set(self.models.keys()):
                model_info = self.models[model_uri]
                if time.time() - model_info.last_used_time > self.server_idle_timeout:
                    logger.info(f'Un-loading mlflow model which is not used for too long: {model_uri}\n'
                                f'Process id: {model_info.process.pid}')
                    self._remove_model(model_uri)
            self.last_cleanup_time = time.time()
        finally:
            self.lock.release()

    def predict(self, model_uri: str, model_input) -> List:
        self.lock.acquire()
        try:
            model_info = self.models.get(model_uri)

            if not model_info:
                self._init_model(model_uri)

            model_info = self.models.get(model_uri)

            if not model_info:
                raise Exception(f'Unable to initialize model: {model_uri}')
            if model_info.process.poll() is not None:
                raise Exception(f'Model initialization was ok but the model server has quit unexpectedly: {model_uri}')

            res = predict_on_server(model_info.unix_socket_path, model_input, self.predict_timeout)

            model_info.last_used_time = time.time()

            self._ensure_watcher_running()

            return res
        finally:
            self.lock.release()
