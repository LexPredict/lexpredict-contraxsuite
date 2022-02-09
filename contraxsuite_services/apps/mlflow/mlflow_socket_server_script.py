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

import os
import pickle
import tempfile
import time
from socketserver import StreamRequestHandler, UnixStreamServer

from mlflow.models import Model
from mlflow.pyfunc import load_model
from mlflow.pyfunc import scoring_server

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


"""
This script is copied to the MLFlow models dirs and used as a simple unix socket server.
Python environment available to this script may be either the nested Contraxsuite virtualenv
or the model's Conda env.
If modifying this script - avoid using any non-standard imports except mlflow.
MLFlow library is installed into each model environment before running it.
"""

UNIX_SOCKET_PATH = 'unix_socket_path'


class PredictRequestHandler(StreamRequestHandler):

    def handle(self):
        model = self.server.model

        model_input = pickle.load(self.rfile)

        try:
            start = time.time()
            model_output = model.predict(model_input)
            print(f'{self.server.model_path} predict in: {time.time() - start} s')
            pickle.dump(model_output, self.wfile)
        except Exception as ex:
            pickle.dump(ex, self.wfile)

        self.server.last_req_time = time.time()


class Server(UnixStreamServer):

    def __init__(self, server_address,
                 RequestHandlerClass,
                 shutdown_if_no_requests_timeout: int = 10,
                 bind_and_activate=True):
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
        self.last_req_time = None
        self.shutdown_if_no_requests_timeout = shutdown_if_no_requests_timeout

    def serve_forever(self, poll_interval=0.5):
        self.last_req_time = time.time()
        super().serve_forever(poll_interval)

    def service_actions(self):
        if self.shutdown_if_no_requests_timeout \
                and time.time() - self.last_req_time > self.shutdown_if_no_requests_timeout:
            print('No new requests appeared for too long. Shutting down.')
            self._BaseServer__shutdown_request = True


def serve(model_path: str, unix_socket_path: str, shutdown_if_no_requests_after_sec: int = 60):
    """
    Serve mlflow pyfunc model via a unix file socket.
    Expects pickled model input, responds with either pickled output or pickled exception.
    :param model_path: Local model path (server model path).
    :param unix_socket_path: Unix file socket path.
    :param shutdown_if_no_requests_after_sec:
    :return:
    """
    model_path = model_path or os.environ.get(scoring_server._SERVER_MODEL_PATH)

    unix_socket_path = unix_socket_path or os.environ.get(UNIX_SOCKET_PATH) or tempfile.NamedTemporaryFile().name
    model = load_model(model_path)  # type: Model
    print(f'Serving model: {model_path}\n'
          f'at: {unix_socket_path}\n'
          f'Process id: {os.getpid()}')

    try:
        os.unlink(unix_socket_path)
    except OSError:
        if os.path.exists(unix_socket_path):
            raise

    server = Server(unix_socket_path, PredictRequestHandler,
                    shutdown_if_no_requests_timeout=shutdown_if_no_requests_after_sec)
    server.model = model
    server.model_path = model_path
    server.serve_forever()


if __name__ == '__main__':

    # "click" is not always available inside the model env - so simply reading from sys.argv

    import sys

    model_path = sys.argv[1]
    unix_socket_path = sys.argv[2]

    if len(sys.argv) > 3:
        timeout = sys.argv[3]
    else:
        timeout = None

    serve(model_path=model_path, unix_socket_path=unix_socket_path, shutdown_if_no_requests_after_sec=timeout)
