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

"""
OCR scanned pdf, image to text.
Also convert doc, docx, odt, pdf to text.

INSTALLATION:
  sudo apt-get install python-dev libxml2-dev libxslt1-dev
               antiword unrtf poppler-utils pstotext tesseract-ocr flac
               ffmpeg lame libmad0 libsox-fmt-mp3 sox libjpeg-dev

  pip install textract

NOTE: process(path, method='pdfminer') gives
  "ShellError: The command `pdf2txt.py /path-to-a-file`
   failed because the executable
   `pdf2txt.py` is not installed on your system."

  method='tesseract' works fine

NOTE: perhaps we can use pdf2pdfa to convert scanned pdf into text
to improve quality of output text.
"""

# Standard imports
import importlib
import os
import re

from textract import exceptions, parsers

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.2/LICENSE"
__version__ = "1.2.2"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

EXTENSION_SYNONYMS = {
    ".jpe": ".jpg",
    ".jpeg": ".jpg",
    ".htm": ".html",
    "": ".txt",
    ".tif": ".tiff",
}

DEFAULT_ENCODING = 'utf_8'


def process(filename, encoding=DEFAULT_ENCODING, ext: str = None, **kwargs):
    """
    Try importing textract parser according to the provided extension or to the extension
    of the specified file name and parsing the file with it.

    This method is mostly copy-paste of the textract "process" method with support of
    user-specified extensions.

    :param filename:
    :param encoding:
    :param ext:
    :param kwargs:
    :return:
    """
    if not os.path.exists(filename):
        raise exceptions.MissingFileError(filename)

    if not ext:
        _, ext = os.path.splitext(filename)
        ext = ext.lower()

    ext = EXTENSION_SYNONYMS.get(ext, ext)

    rel_module = ext + '_parser'
    importlib.import_module('textract.parsers')
    filetype_module = importlib.import_module(rel_module, 'textract.parsers')
    parser = filetype_module.Parser()
    return parser.process(filename, encoding, **kwargs)


def process_text(text):
    """
    Simple text regular expression.
    :param text:
    :return:
    """
    text = re.sub(r'\s*\n+\s*', '\n', text)
    return text


def textract2text(path, language='eng', ext: str = None):
    # extract text as bytes
    text = process(path, ext=ext, method='tesseract', language=language)
    # convert to string
    text = text.decode('utf-8')
    # process text - remove extra symbols, etc.
    # text = process_text(text)
    return text
