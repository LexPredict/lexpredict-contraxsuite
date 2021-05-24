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

import pickle
import socket
import sys
import time

import click
import pandas as pd

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


"""
Client module to connect to the MLFlow model servers started by the server manager (mlflow_model_manager.py).
"""


def predict_on_server(unix_socket_path: str, model_input, timeout_in_seconds: int = 60):
    """
    Connect to the simple socket server (mlflow_socket_server_script.py) listening at "unix_socket_path"
    and request the model prediction on the passed "model_input".
    :param unix_socket_path:
    :param model_input:
    :param timeout_in_seconds:
    :return:
    """
    data = pickle.dumps(model_input)
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(timeout_in_seconds)

    try:
        sock.connect(unix_socket_path)
        sock.sendall(data)

        data_chunks = []

        try:
            data_chunk = sock.recv(4096)
            while data_chunk:
                data_chunks.append(data_chunk)
                data_chunk = sock.recv(4096)
        except socket.timeout as e:
            if e.args[0] == 'timed out':
                raise TimeoutError('Timeout waiting for mlflow model server response.')
            raise RuntimeError('Mlflow server closed connection.')

        data = b''.join(data_chunks)

        res = pickle.loads(data)

        if isinstance(res, Exception):
            raise res
        return res
    finally:
        sock.close()


@click.command('Mlflow socket server client. Connects to mlflow simple server via unix file socket, '
               'sends pickled model input, prints un-pickled output.\n'
               'Reads model input from stdin. Format: pandas dataframe encoded in json with "records" orient.\n'
               'Example: [{"text": "Governing law"}]')
@click.option('--unix-socket-path', help='Unix socket path.')
@click.pass_context
def run(click_ctx, unix_socket_path):
    if not unix_socket_path:
        click.echo(click_ctx.get_help())
        click_ctx.exit()

    model_input = pd.read_json(sys.stdin, orient='records')
    start = time.time()
    model_output = predict_on_server(unix_socket_path, model_input, timeout_in_seconds=5)
    print(f'Send/predict/recv in: {time.time() - start} s')
    print(model_output)


if __name__ == '__main__':
    run()
