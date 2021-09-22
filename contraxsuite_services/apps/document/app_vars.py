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

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def validate_table_parser(table_parser: str):
    all_parsers = {'lattice', 'stream', 'area_lattice', 'area_stream'}
    if table_parser not in all_parsers:
        values = ', '.join(list(all_parsers))
        raise RuntimeError(f'''Value should be one of the following: {values}.''')


ADMIN_RUNNING_TASKS_VALIDATION_ENABLED = AppVar.set(
    'Document', 'admin_running_tasks_validation_enabled', True,
    'Prevents critical changes if user tasks running')

MAX_DOCUMENT_SIZE = AppVar.set(
    'Document', 'max_document_size', 50,
    'Enables maximum document file size for uploading, Mb',
    system_only=False)

MAX_ARCHIVE_SIZE = AppVar.set(
    'Document', 'max_archive_size', 100,
    'Enables maximum archive file size for uploading, Mb',
    system_only=False)

PREPROCESS_DOCTEXT_LINEBREAKS = AppVar.set(
    'Document', 'preprocess_doctext_linebreaks', True,
    'Enables / disables removing extra line breaks in uploaded document',
    system_only=False)

PREPROCESS_DOCTEXT_PUNCT = AppVar.set(
    'Document', 'preprocess_doctext_punct', False,
    'Fix anomalies in quotes and spaces in uploaded document',
    system_only=False)

LOCATE_TEXTUNITTAGS = AppVar.set(
    'Document', 'locate_text_unit_tags', False,
    'Enables storing text unit tags during parsing a document',
    system_only=False)

LOCATE_TEXTUNITPROPERTIES = AppVar.set(
    'Document', 'locate_text_unit_properties', False,
    'Enables storing text unit properties during parsing a document',
    system_only=False)

OCR_ENABLE = AppVar.set(
    'Document', 'ocr_enable', True,
    'Enables / disables OCR when loading documents',
    system_only=False)

TABLE_DETECTION_ENABLE = AppVar.set(
    'Document', 'table_detection_enable', True,
    'Enables / disables table detection when loading documents',
    system_only=False)

TABLE_DETECTION_METHOD = AppVar.set(
    'Document', 'table_detection_method', 'area_stream',
    '''<ul>
       <li><code>area_stream</code> - first detect table areas using cv2, next detect tables in the areas 
           with Camelot: stream detector. Can detect borderless tables.</li>
       <li><code>area_lattice</code>first detect table areas using cv2, next detect tables in the areas 
           with Camelot: lattice detector. Detects only tables with borders.</li>
       <li><code>lattice</code> - detects only tables with border, decent detection quality.</li>
       <li><code>stream</code> - detect tables with or without borders, may produce unexpected results.</li>
    </ul>''',
    system_only=False,
    validator=validate_table_parser)

DESKEW_ENABLE = AppVar.set(
    'Document', 'deskew_enable', True,
    'Enables / disables automatic correction of the rotated (skewed) pages when loading documents',
    system_only=False)

PDF_COORDINATES_DEBUG_ENABLE = AppVar.set(
    'Document', 'pdf_coordinates_debug_enable', False,
    'Enables / disables rendering a rectangle for each character in PDF documents '
    '- for the coordinates debug purposes.',
    system_only=False)

DOCUMENT_LOCALE = AppVar.set(
    'Document', 'document_locale', None,
    'Sets default document locale. Use ISO-639 codes, e.g., "en_US", "en_GB", or "de"',
    system_only=False)

OCR_FILE_SIZE_LIMIT = AppVar.set(
    'Document', 'ocr_file_size_limit', 100,
    'Max file size enabled (MB) for OCR',
    system_only=False)

OCR_PAGE_TIMEOUT = AppVar.set(
    'Document', 'ocr_page_timeout', 60,
    'Document per-page OCR timeout, seconds',
    system_only=False)

REMOVE_OCR_LAYERS = AppVar.set(
    'Document', 'remove_ocr_layers', False,
    'Remove OCR layers on PDF pages',
    system_only=False)

MIN_NOT_PLAIN_FILE_SIZE = AppVar.set(
    'Document', 'min_not_plain_file_size', 1024,
    'Mint file size (bytes) to try extracting text with Tika / Textract etc.',
    system_only=False)

MSWORD_TO_TEXT_ENABLE = AppVar.set(
    'Document', 'msword_to_text_enable', True,
    'Enables / disables parsing MS Word documents with python-docx',
    system_only=False)

ALLOW_DUPLICATE_DOCS = AppVar.set(
    'Document', 'allow_duplicate_documents', False,
    "If True, additional uploads of the same file name and same content " +
    "will be allowed and copy 01, copy 02, etc will be added to the name. " +
    "If False, you will get an error rejecting the upload of duplicate documents.",
    system_only=False, target_type=bool)

DETECT_CONTRACT = AppVar.set(
    'Document', 'detect_contract', True,
    'Check if document is a contract',
    system_only=False
)

DETECT_CONTRACT_TYPE = AppVar.set(
    'Document', 'detect_contract_type', False,
    'Identify document contract type',
    system_only=False
)

ENABLE_PROVISION_LEVEL_REVIEW = AppVar.set(
    'Document', 'enable_provision_level_review', False,
    'Provision Level Review on/off.',
    system_only=False
)

CSV_DETECTOR_COMPANIES = AppVar.set(
    'Document', 'csv_detector_companies',
    'LLC,,Corp,,LP,,Inc,,Ltd,,Corporation,,Limited,,Co,,S.A',
    '''CSV Detector - company abbreviations. Use two commas to separate values. Example:<br/>
       <code>"LLC,,Corp,,LP,,Inc,,Ltd,,Corporation,,Limited,,Co,,S.A"</code>
    ''',
    system_only=False
)

CSV_DETECTOR_CONJUNCTIONS = AppVar.set(
    'Document', 'csv_detector_conjunctions',
    'and,,the,,&',
    '''CSV Detector - conjunctions. Use two commas to separate values. Example:<br/>
       <code>"and,,the,,&"</code>''',
    system_only=False
)

ALLOW_REMOVE_DOC_TYPE_WITH_PROJECT = AppVar.set(
    'Document', 'allow_remove_doc_type_with_project', False,
    'Allow to remove document types with projects.')

MAX_DOCUMENTS_TO_EXPORT_SIZE_HTTP = AppVar.set(
    'Document', 'max_documents_to_export_size', 20,
    'Maximum total size of document files (Mb) to export as zip via http response.',
    system_only=False)

MAX_DOC_SIZE_IN_MAIL_ARCHIVE = AppVar.set(
    'Document', 'max_doc_size_per_mail_archive', 50,
    'Maximum total size of document files per one attached archive, MB.',
    system_only=False)

CONTRACT_TYPE_FILTER = AppVar.set(
    'Document', 'contract_type_filter',
    '{"min_prob": 0.05, "max_closest_percent": 100}',
    "Set contract type as 'UNKNOWN' if either the probability is too low or " +
    "the next detected type has about the same probability",
    system_only=False
)
