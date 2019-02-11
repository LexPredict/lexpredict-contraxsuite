import json
import os
import re
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Dict, Optional

import requests


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
            data.append({'id': f, 'document_number': f[:-4]})
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
