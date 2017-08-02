# -*- coding: utf-8 -*-
__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0/LICENSE.pdf"
__version__ = "1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@lexpredict.com"

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
import re
from textract import process


def process_text(text):
    """
    Simple text regular expression.
    :param text:
    :return:
    """
    text = re.sub(r'\s*\n+\s*', '\n', text)
    return text


def textract2text(path, language='eng'):
    # extract text as bytes
    text = process(path, method='tesseract', language=language)
    # convert to string
    text = text.decode('utf-8')
    # process text - remove extra symbols, etc.
    # text = process_text(text)
    return text
