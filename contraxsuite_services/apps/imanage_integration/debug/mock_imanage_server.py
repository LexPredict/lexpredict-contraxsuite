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

import json
import os
import re
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Dict, Optional

import requests

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class MockServerRequestHandler(BaseHTTPRequestHandler):
    def resp(self, code: int, headers: Optional[Dict], body: Dict):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        if headers:
            for k, v in headers.items():
                self.send_header(k, v)
        self.end_headers()
        if body:
            self.wfile.write(json.dumps(body, indent=True).encode('utf-8'))

    def do_login(self):
        self.resp(requests.codes.ok, None, {'X-Auth-Token': 'the_secret_token'})

    def do_search(self):
        data = []
        for f in os.listdir('./data'):
            data.append({'id': f, 'document_number': f[:-4], 'custom1': f[:4], 'custom2': f[5:8]})
        self.resp(requests.codes.ok, None, {'data': data})

    def do_download(self, doc_id: str):
        self.send_response(requests.codes.ok)
        self.send_header('Content-Disposition', 'attachment; filename="' + doc_id + '"')
        self.end_headers()
        with open('./data/' + doc_id, 'rb') as f:
            while True:
                b = f.read(1024)
                if not b:
                    break
                self.wfile.write(b)

    download_re = re.compile(r'/api/v1/documents/(?P<doc_id>[^/]+)/download')

    def do_PUT(self):
        # Process an HTTP GET request and return a response with an HTTP 200 status.
        if self.path == '/api/v1/session/login':
            self.do_login()

    def do_GET(self):
        # Process an HTTP GET request and return a response with an HTTP 200 status.
        if self.path.startswith('/api/v1/documents/search'):
            self.do_search()
        else:
            m = self.download_re.search(self.path)
            if m:
                self.do_download(m.group('doc_id'))
            return


def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    address, port = s.getsockname()
    s.close()
    return port


class MockIManageServer(object):
    @classmethod
    def start(cls):
        cls.mock_server_port = 65534  # get_free_port()
        cls.mock_server = HTTPServer(('localhost', cls.mock_server_port), MockServerRequestHandler)
        cls.mock_server_thread = Thread(target=cls.mock_server.serve_forever)
        cls.mock_server_thread.setDaemon(False)
        cls.mock_server_thread.start()
        print('Started mock iManage server at localhost:' + str(cls.mock_server_port))


if __name__ == '__main__':
    MockIManageServer.start()
