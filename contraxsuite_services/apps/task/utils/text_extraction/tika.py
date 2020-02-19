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

# Tika imports
import os
import tempfile
from typing import Dict

from tika.parser import _parse
from tika.tika import getRemoteFile, callServer

from apps.common.log_utils import ProcessLogger
from apps.common.processes import read_output
from apps.common.singleton import Singleton

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


@Singleton
class TikaParametrizedParser:
    # flag defines how Tika parses passed file
    TIKA_URL_FLAG_MODE = 'pdf-parse'

    # the same flag as environment variable
    TIKA_ENV_VAR_FLAG_MODE = 'LEXNLP_TIKA_PARSER_MODE'

    # flag's value - parse only PDF
    TIKA_MODE_OCR = 'pdf_ocr'

    # flag's value - parse both PDF and scanned images
    TIKA_MODE_PDF_ONLY = 'pdf_only'

    def __init__(self):
        self.tika_files_path = tempfile.gettempdir()
        self.tika_jar_path = tempfile.gettempdir()

        from django.conf import settings
        jar_base_path = settings.JAR_BASE_PATH

        tika_cls_name = 'org.apache.tika.cli.TikaCLI'
        tika_cp = ':'.join([os.path.join(jar_base_path, jar) for jar in settings.TIKA_JARS])

        conf_full_path = os.path.join(jar_base_path, 'tika.config')
        self.tika_start_command_list = ['java',
                                        '-cp', tika_cp,
                                        '-Dsun.java2d.cmm=sun.java2d.cmm.kcms.KcmsServiceProvider',
                                        tika_cls_name,
                                        f'--config={conf_full_path}']

    def parse_file_local(self,
                         local_path: str,
                         original_file_name: str,
                         timeout: int = 60,
                         encoding_name: str = 'utf-8',
                         logger: ProcessLogger = None,
                         enable_ocr: bool = True) -> Dict:
        mode_flag = self.TIKA_MODE_OCR if enable_ocr else self.TIKA_MODE_PDF_ONLY
        os.environ[self.TIKA_ENV_VAR_FLAG_MODE] = mode_flag

        cmd = self.tika_start_command_list + ['-J', '-t', f'-e{encoding_name}', local_path]

        def err(line):
            logger.info(f'TIKA parsing {original_file_name}:\n{line}')

        text = read_output(cmd, stderr_callback=err, encoding=encoding_name, timeout_sec=timeout) or ''

        try:
            return _parse((200, text))
        except Exception as ex:
            text_sample = text[:255] if text and isinstance(text, str) else str(text)
            raise Exception('Error in parse_default_pdf_ocr -> _parse(). Text:\n' +
                            text_sample) from ex

    def parse_file_on_server(self,
                             option: str,
                             url_or_path: str,
                             server_endpoint: str = None,
                             enable_ocr: bool = True) -> Dict:
        parse_mode = self.TIKA_MODE_OCR if enable_ocr else self.TIKA_MODE_PDF_ONLY
        return self.parse(option, url_or_path, server_endpoint,
                          extra_headers={'pdf-parse': parse_mode})

    def parse(self,
              option: str,
              url_or_path: str,
              server_endpoint: str = None,
              verbose: int = 0,
              tika_server_jar: str = None,
              response_mime_type: str = 'application/json',
              services: dict = None,
              raw_response: bool = False,
              extra_headers: Dict[str, str] = None) -> Dict:

        services = services if services else \
            {'meta': '/meta', 'text': '/tika', 'all': '/rmeta/text'}
        tika_server_jar = tika_server_jar if tika_server_jar else self.tika_jar_path
        server_endpoint = server_endpoint if server_endpoint else self.server_endpoint

        path, file_type = getRemoteFile(url_or_path, self.tika_files_path)
        service = services.get(option, services['all'])
        if service == '/tika':
            response_mime_type = 'text/plain'
        content_path = self.make_content_disposition_header(path)

        headers = {
            'Accept': response_mime_type,
            'Content-Disposition': content_path
        }
        if extra_headers:
            headers = {**headers, **extra_headers}

        status, response = callServer('put',
                                      server_endpoint,
                                      service,
                                      open(path, 'rb'),
                                      headers,
                                      verbose,
                                      tika_server_jar,
                                      rawResponse=raw_response)

        if file_type == 'remote':
            os.unlink(path)
        return _parse((status, response))

    def make_content_disposition_header(self, fn):
        return 'attachment; filename=%s' % os.path.basename(fn)


parametrized_tika_parser = TikaParametrizedParser()
