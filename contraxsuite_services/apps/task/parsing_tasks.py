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

from subprocess import CalledProcessError
from typing import Any, List, Optional

import tabula
from pandas import DataFrame

import settings
from apps.task.utils.marked_up_text import MarkedUpText
from apps.task.utils.text_extraction.tika.tika_parsing_wrapper import TikaParsingWrapper
from apps.task.utils.text_extraction.xml_wordx.xml_wordx_extractor import XmlWordxExtractor
from apps.task.utils.text_extraction.textract import textract2text
from apps.common.log_utils import ProcessLogger
from traceback import format_exc

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class ParsingTaskParams:
    def __init__(self,
                 logger: ProcessLogger,
                 file_path: str,
                 ext: str,
                 original_file_name: str,
                 task: Any,
                 propagate_exceptions: bool = True,
                 enable_ocr: bool = True):
        """
        :param logger: used to log errors / warnings
        :param file_path: file or URL with content to be parsed (temporary path)
        :param original_file_name: original file name
        :param propagate_exceptions: should throw exceptions
        :param enable_ocr: enable / disable OCR
        :param ext: original file extension
        """
        self.logger = logger
        self.file_path = file_path
        self.ext = ext
        self.original_file_name = original_file_name
        self.propagate_exceptions = propagate_exceptions
        self.enable_ocr = enable_ocr
        self.task = task


class DocumentParsingResults:

    def __init__(self,
                 text: Optional[MarkedUpText] = None,
                 parser: Optional[str] = None,
                 metadata: Any = None,
                 tables: Optional[List[DataFrame]] = None):
        self.text = text
        self.parser = parser
        self.metadata = metadata
        self.tables = tables

    def is_empty(self):
        return not self.text or not self.text.text

    def get_text(self):
        return self.text.text if self.text else ''


class BaseDocumentParser:
    """
    Each parser extracts text (try_parse_document) and returns
    tuple of (text, parser_name, metadata).

    If this parser couldn't process this file, it returns None, None, None
    Besides the parser can fill lists of tables.
    """

    def __init__(self):
        self.tables = []  # type:List[DataFrame]

    def try_parse_document(self, ptrs: ParsingTaskParams) -> DocumentParsingResults:
        raise NotImplementedError()

    def parse_pdf_tables(self, ptrs: ParsingTaskParams):
        if ptrs.ext == '.pdf':
            try:
                document_tables = tabula.read_pdf(
                    ptrs.file_path,
                    multiple_tables=True,
                    pages='all')
                self.tables = [
                    [list(j) for j in list(i.fillna('').to_records(index=False))
                     if not i.empty]
                    for i in document_tables if not i.empty]
            except CalledProcessError:
                pass


class TikaDocumentParser(BaseDocumentParser):
    METADATA_OLD_NEW_KEY = {'dc:title': 'title'}

    def __init__(self):
        super().__init__()

    def try_parse_document(self, ptrs: ParsingTaskParams) -> DocumentParsingResults:
        """
        :return: (text, 'tika', metadata)
        """

        # set OCR strategy (environment var)
        if ptrs.logger:
            ptrs.logger.info(f'Trying TIKA for file: {ptrs.original_file_name}')
        if settings.TIKA_DISABLE:
            if ptrs.logger:
                ptrs.logger.info('TIKA is disabled in config')
            return DocumentParsingResults()

        from apps.document.app_vars import TIKA_TIMEOUT
        timeout = TIKA_TIMEOUT.val
        try:
            # here we command Tika to use OCR for image-based PDFs
            # or switch to 'native' call parser.from_file(file_path, settings. ...)

            # this app var is imported here in lazy manner to prevent
            # issues when tasks.py is imported in migrations before the tables for app vars are created
            from apps.document.app_vars import TIKA_SERVER_ENDPOINT
            tika_server_endpoint = TIKA_SERVER_ENDPOINT.val
            tika_parsing_wrapper = TikaParsingWrapper()
            if tika_server_endpoint:
                if ptrs.logger:
                    ptrs.logger.info(f'TIKA server endpoint: {tika_server_endpoint}')
                # call Tika as server
                data = tika_parsing_wrapper.parse_file_on_server(
                    'all', ptrs.file_path, tika_server_endpoint,
                    enable_ocr=ptrs.enable_ocr)
            else:
                from apps.document.app_vars import TIKA_PARSE_MODE
                # or execute Tika jar
                parse_function = tika_parsing_wrapper.parse_file_local_xhtml \
                    if TIKA_PARSE_MODE.val == 'xhtml' else tika_parsing_wrapper.parse_file_local_plain_text

                data = parse_function(
                    local_path=ptrs.file_path,
                    original_file_name=ptrs.original_file_name,
                    task=ptrs.task,
                    timeout=timeout,
                    logger=ptrs.logger,
                    enable_ocr=ptrs.enable_ocr)

            if data and getattr(data, 'text', None) and len(data.text) >= 100:
                if data.tables:
                    self.tables = [t.serialize_in_dataframe(data.text) for t in data.tables]
                else:
                    self.parse_pdf_tables(ptrs)
                pars_result = DocumentParsingResults(
                    data, 'tika', data.meta, self.tables)
                self.post_process_metadata(pars_result)
                return pars_result
            else:
                ptrs.logger.error('TIKA returned too small text for file: ' +
                                  ptrs.original_file_name)
                return DocumentParsingResults()
        except Exception as ex:
            ptrs.logger.error('Caught exception while trying to parse file with'
                              f'Tika: {ptrs.original_file_name}\n{format_exc()}, '
                              f'timeout is: {timeout}')
            if ptrs.propagate_exceptions:
                raise ex
            return DocumentParsingResults()

    @staticmethod
    def post_process_metadata(result: DocumentParsingResults) -> None:
        """
        Unify some parameter names in metadata
        """
        if not result.metadata:
            return
        for old_key in TikaDocumentParser.METADATA_OLD_NEW_KEY:
            if old_key not in result.metadata:
                continue
            new_key = TikaDocumentParser.METADATA_OLD_NEW_KEY[old_key]
            if new_key not in result.metadata:
                result.metadata[new_key] = result.metadata[old_key]
                del result.metadata[old_key]


class TextractDocumentParser(BaseDocumentParser):
    def __init__(self):
        super().__init__()

    def try_parse_document(self, ptrs: ParsingTaskParams) -> DocumentParsingResults:
        if ptrs.logger:
            ptrs.logger.info('Trying Textract for file: ' +
                             ptrs.original_file_name)
        try:
            text = textract2text(ptrs.file_path, ext=ptrs.ext)
            self.parse_pdf_tables(ptrs)
            return DocumentParsingResults(
                MarkedUpText(text), 'textract', None, self.tables)
        except Exception as ex:
            if ptrs.logger:
                ptrs.logger.error('Caught exception while trying to parse file '
                                  f'with Textract: {ptrs.original_file_name}'
                                  f'\n{format_exc()}')
            if ptrs.propagate_exceptions:
                raise ex
            return DocumentParsingResults()


class XmlWordxDocumentParser(BaseDocumentParser):
    def __init__(self):
        super().__init__()

    def try_parse_document(self, ptrs: ParsingTaskParams) -> DocumentParsingResults:
        """
        :return: (text, 'msword', None)
        """
        try:
            log_func = lambda s: ptrs.logger.info(s) if ptrs.logger else None
            xtractor = XmlWordxExtractor(log_func=log_func)
            if not xtractor.can_process_file(ptrs.original_file_name):
                return DocumentParsingResults()

            if ptrs.logger:
                ptrs.logger.info('Trying MS Word extract for file: ' +
                                 ptrs.original_file_name)

            return DocumentParsingResults(
                MarkedUpText(xtractor.parse_file(ptrs.file_path)),
                'msword', None, xtractor.tables)
        except Exception as ex:
            if ptrs.logger:
                ptrs.logger.info('Caught exception while trying to parse file '
                                 f'with MS Word parser: {ptrs.original_file_name}'
                                 f'\n{format_exc()}')
            if ptrs.propagate_exceptions:
                raise ex
            return DocumentParsingResults()


class PlainTextDocumentParser(BaseDocumentParser):
    def __init__(self):
        super().__init__()

    def try_parse_document(self, ptrs: ParsingTaskParams) -> DocumentParsingResults:
        """
        :return: (text, 'plain text', None)
        """
        if ptrs.ext.strip(' .').lower() != 'txt':
            return DocumentParsingResults()
        if ptrs.logger:
            ptrs.logger.info('Trying plain text extraction for file: ' +
                             ptrs.original_file_name)
        try:
            import magic
            f = magic.Magic(mime=True)
            mime_type = f.from_file(ptrs.file_path)
            if mime_type == 'text/plain':
                import chardet
                with open(ptrs.file_path, "rb") as fr:
                    bytes = fr.read()
                enc_data = chardet.detect(bytes)
                if enc_data['confidence'] > 0.9:
                    txt = bytes.decode(enc_data['encoding'])
                    rst = DocumentParsingResults(text=MarkedUpText(txt), parser='plain text')
                    return rst
        except Exception as ex:
            if ptrs.logger:
                ptrs.logger.info('Caught exception while trying to parse file '
                                 f'with plain text parser: {ptrs.original_file_name}'
                                 f'\n{format_exc()}')
            if ptrs.propagate_exceptions:
                raise ex
        return DocumentParsingResults()
