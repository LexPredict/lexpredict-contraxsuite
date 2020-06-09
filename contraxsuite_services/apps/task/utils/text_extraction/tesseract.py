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

# Standard imports
import os
import subprocess

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.6.0/LICENSE"
__version__ = "1.6.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


# TODO: Allow configuration-based tesseract path.
TESSERACT_PATH = "/usr/bin/"


def process_tesseract_file(input_file_path, output_file_path,
                           tesseract_language="eng", tesseract_whitelist=None):
    """
    Process a document with tesseract.
    :param input_file_path: path to input document file
    :param output_file_path: path to output document file
    :param tesseract_language: language model
    :param tesseract_whitelist:
    :return: return code
    """
    # Setup command arguments
    args_tesseract = [os.path.join(TESSERACT_PATH, "tesseract"),
                      "-l", str(tesseract_language)]
    if tesseract_whitelist:
        args_tesseract.extend(["-c", 'tessedit_char_whitelist={0}'.format(tesseract_whitelist)])
    args_tesseract.extend([input_file_path, output_file_path])

    # Execute command
    proc_tesseract = subprocess.Popen(args_tesseract, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
    proc_tesseract_out, proc_tesseract_err = proc_tesseract.communicate()
    proc_tesseract.wait()

    # Write stdout/err/retcode
    if proc_tesseract_out:
        with open(os.path.join(os.path.dirname(output_file_path), "tesseract-stdout"), "wb") as f:
            f.write(proc_tesseract_out)
    if proc_tesseract_err:
        with open(os.path.join(os.path.dirname(output_file_path), "tesseract-stderr"), "wb") as f:
            f.write(proc_tesseract_err)
    with open(os.path.join(os.path.dirname(output_file_path), "tesseract-retcode"), "wb") as f:
        f.write(str(proc_tesseract.returncode).encode("utf-8"))

    # Change path back and return
    return proc_tesseract.returncode
