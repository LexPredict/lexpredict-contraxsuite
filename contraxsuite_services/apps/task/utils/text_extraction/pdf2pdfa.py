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

import os
import subprocess
import tempfile

import pdf2image
from apps.common.processes import read_output

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def pdf2pdfa_with_ocrmypdf(input_file_path, output_file_path, language='eng', force_ocr=False):
    """
    Process method relying on ocrmypdf - just a wrapper
    :param input_file_path: str
    :param output_file_path: str
    :param language: str [eng]
    :param force_ocr: bool [eng]
    :return:

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
    WARN:
        ocrmypdf depends on Ghostscript.js which is under GNU Affero General Public License (AGPL)
    """
    cmd_args = ['ocrmypdf', input_file_path, output_file_path, '-l', language]
    if force_ocr:
        cmd_args.append('--force-ocr')
    subprocess.check_call(cmd_args)


def _pdf2ppm(input_file_path, work_dir, dpi_x=200, dpi_y=200, ppm_file_prefix='page'):
    """
    Convert PDF to a bunch of .ppm files using pdftoppm
    :param input_file_path:
    :param tmp_dir:
    :param dpi_x:
    :param dpi_y:
    :param ppm_file_prefix:
    :return:
    """
    original_path = os.getcwd()
    if not os.path.exists(work_dir):
        os.makedirs(work_dir)
    os.chdir(work_dir)

    cmd_args = ['pdftoppm', '-rx', str(dpi_x), '-ry', str(dpi_y), input_file_path, ppm_file_prefix]
    subprocess.check_call(cmd_args)

    ppm_list = [os.path.join(work_dir, i) for i in sorted(os.listdir(work_dir)) if
                i.startswith(ppm_file_prefix)]
    ppm_list_file_path = os.path.join(work_dir, 'ppm_list.txt')
    with open(ppm_list_file_path, 'w') as f:
        f.write('\n'.join(ppm_list))

    os.chdir(original_path)

    return ppm_list_file_path


def pdf2img(input_file_path, work_dir, **pdf2image_kwargs):
    """
    Convert PDF to a bunch of image files using pdf2image
    :param input_file_path: str
    :param work_dir: str
    :param image_format: str ppm/jpg/png
    :return: str - path to a file with list of images' paths
    """
    pdf2image.convert_from_path(input_file_path,
                                output_folder=work_dir,
                                **pdf2image_kwargs)
    img_list = [os.path.join(work_dir, i) for i in sorted(os.listdir(work_dir))]
    img_list_file_path = os.path.join(work_dir, 'img_list.txt')
    with open(img_list_file_path, 'w') as f:
        f.write('\n'.join(img_list))
    return img_list_file_path


def _pdf2pdfa(input_file_path, output_file_path, language='eng', output_types=['pdf']):
    """
    Convert scanned PDF into searchable PDF-A or optionally into hOCR or txt (see output_types)
    :param input_file_path:
    :param output_file_path:
    :param language:
    :param output_types: List['pdf', 'hocr', 'txt']
    :return:
    """
    with tempfile.TemporaryDirectory() as tmp_dir:

        pdf2image_kwargs = dict(fmt='jpg', jpegopt={'quality': 50})
        img_list_file_path = pdf2img(input_file_path, work_dir=tmp_dir, **pdf2image_kwargs)

        cmd_args = ['tesseract', '-l', str(language), img_list_file_path, output_file_path]
        for ot in output_types:
            cmd_args += ['-c', f'tessedit_create_{ot}=1']

        subprocess.check_call(cmd_args)

        # rename file.pdf.alt.pdf into file.pdf.alt
        for ot in output_types:
            os.rename(output_file_path + f'.{ot}', output_file_path)


def pdf2pdfa(task, input_file_path, output_file_path,
             language='eng', output_types=['pdf'], logger=None, timeout=600):
    """
    Convert scanned PDF into searchable PDF-A or optionally into hOCR or txt (see output_types)
    :param task: Task
    :param input_file_path:
    :param output_file_path:
    :param language:
    :param output_types: List['pdf', 'hocr', 'txt']
    :param logger: ProcessLogger
    :param timeout: sec
    :return:
    """
    with tempfile.TemporaryDirectory() as tmp_dir:

        pdf2image_kwargs = dict(fmt='jpg', jpegopt={'quality': 50})
        img_list_file_path = pdf2img(input_file_path, work_dir=tmp_dir, **pdf2image_kwargs)

        cmd_args = ['tesseract', '-l', str(language), img_list_file_path, output_file_path]
        for ot in output_types:
            cmd_args += ['-c', f'tessedit_create_{ot}=1']

        def err(line):
            logger.info(f'tesseract converting {img_list_file_path} '
                        f'images into {output_file_path}:\n{line}')

        read_output(cmd_args, stderr_callback=err, timeout_sec=timeout, task=task) or ''

        # rename file.pdf.alt.pdf into file.pdf.alt
        for ot in output_types:
            os.rename(output_file_path + f'.{ot}', output_file_path)
