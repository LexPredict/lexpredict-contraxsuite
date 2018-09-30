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
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.4/LICENSE"
__version__ = "1.1.4"
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
