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

import pandas as pd
import io
import re
import subprocess

from apps.common.processes import read_output

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def process_image_list(out):
    out = out.splitlines()
    out = '\n'.join(out[:1] + out[2:])
    out = re.sub(r'[ ]+', ';', out)
    df = pd.read_csv(io.StringIO(out), sep=';')
    return df[df['type'].isin(['image', 'stencil'])].shape[0] > 0


def _pdf_has_images(file_path):
    """
    Check whether PDF file has images
    :param file_path: str
    :return: bool
    """
    out = subprocess.check_output(['pdfimages', '-list', file_path])
    return process_image_list(out.decode('utf-8'))


def pdf_has_images(file_path, task, logger=None, timeout=600):
    """
    Check whether PDF file has images
    :param file_path: str
    :param task: celery task
    :param logger: ProcessLogger
    :param timeout: timeout sec
    :return: bool
    """

    def err(line):
        logger.info(f'pdfimages parsing {file_path}:\n{line}')

    cmd = ['pdfimages', '-list', file_path]
    out = read_output(cmd, stderr_callback=err, timeout_sec=timeout, task=task) or ''

    return process_image_list(out)
