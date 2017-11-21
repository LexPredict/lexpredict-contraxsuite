# -*- coding: utf-8 -*-

"""
FROM:
    https://ocrmypdf.readthedocs.io/en/latest/introduction.html#about-pdf-a
    OCRmyPDF adds an OCR text layer to scanned PDF files,
    allowing them to be searched or copy-pasted.
    Converts scanned pdf into pdf/a, then we can parse it normally.

INSTALLATION:
    pip install OCRmyPDF
    Ubuntu 16.10 or later: sudo apt-get install ocrmypdf

USAGE:
    ocrmypdf in.pdf out.pdf
"""

# Import
import subprocess

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.3/LICENSE"
__version__ = "1.0.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def process(input_file_path, output_file_path, language='eng'):
    """
    Process method relying on ocrmypdf.

    :param input_file_path:
    :param output_file_path:
    :param language:
    :return:
    """
    subprocess.check_call(['ocrmypdf',
                           input_file_path,
                           output_file_path,
                           '-l', language])
