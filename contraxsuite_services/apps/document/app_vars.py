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

# Project imports
from apps.common.models import AppVar
from django.conf import settings

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.3.0/LICENSE"
__version__ = "1.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


ADMIN_RUNNING_TASKS_VALIDATION_ENABLED = AppVar.set(
    'admin_running_tasks_validation_enabled', True,
    'Prevents critical changes if user tasks running')

TIKA_SERVER_ENDPOINT = AppVar.set(
    'tika_remote_server_endpoint', None,
    'TIKA server endpoint. Example: http://contrax-tika:9998')

TIKA_TIMEOUT = AppVar.set(
    'tika_timeout', settings.TIKA_TIMEOUT,
    'TIKA timeout (default = 3600 s)')

MAX_DOCUMENT_SIZE = AppVar.set(
    'max_document_size', 50,
    'Enables maximum document file size for uploading, Mb')

MAX_ARCHIVE_SIZE = AppVar.set(
    'max_archive_size', 100,
    'Enables maximum archive file size for uploading, Mb')

PREPROCESS_DOCTEXT_LINEBREAKS = AppVar.set(
    'preprocess_doctext_linebreaks', True,
    'Enables / disables removing extra line breaks in uploaded document')

PREPROCESS_DOCTEXT_PUNCT = AppVar.set(
    'preprocess_doctext_punct', False,
    'Fix anomalies in quotes and spaces in uploaded document')

LOCATE_TEXTUNITTAGS = AppVar.set(
    'locate_text_unit_tags', False,
    'Enables storing text unit tags during parsing a document')

LOCATE_TEXTUNITPROPERTIES = AppVar.set(
    'locate_text_unit_properties', False,
    'Enables storing text unit properties during parsing a document')

OCR_ENABLE = AppVar.set(
    'ocr_enable', True,
    'Enables / disables documents OCR by Tika os Textract')

OCR_FILE_SIZE_LIMIT = AppVar.set(
    'ocr_file_size_limit', 100,
    'Max file size enabled (MB) for OCR')

MSWORD_TO_TEXT_ENABLE = AppVar.set(
    'msword_to_text_enable', True,
    'Enables / disables parsing MS Word documents with python-docx')

FORCE_REWRITE_DOC = AppVar.set(
    'force_rewrite_doc', True,
    'Enables / disables rewriting existing documents')

STRICT_PARSE_DATES = AppVar.set(
    'strict_parse_dates', True,
    'Skip values like "C-4-30" if strict mode (True) is on')
