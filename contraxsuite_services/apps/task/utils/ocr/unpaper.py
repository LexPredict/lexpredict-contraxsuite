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
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.5/LICENSE"
__version__ = "1.0.7"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

# TODO: Allow configuration-based unpaper path.
UNPAPER_PATH = "/usr/bin/"


def process_unpaper_file(input_file_path, output_file_path, unpaper_dpi=300):
    """
    Process a document with unpaper.
    :param input_file_path: path to input document file
    :param output_file_path: path to output document file
    :param unpaper_dpi: DPI to export at
    :return: return code
    """
    # Setup command arguments and execute
    args_unpaper = [os.path.join(UNPAPER_PATH, "unpaper"),
                    "--dpi", str(unpaper_dpi),
                    input_file_path, output_file_path]
    proc_unpaper = subprocess.Popen(args_unpaper, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc_unpaper_out, proc_unpaper_err = proc_unpaper.communicate()
    proc_unpaper.wait()

    # Write stdout/err/retcode
    if proc_unpaper_out:
        with open(os.path.join(os.path.dirname(output_file_path), "unpaper-stdout"), "wb") as f:
            f.write(proc_unpaper_out)
    if proc_unpaper_err:
        with open(os.path.join(os.path.dirname(output_file_path), "unpaper-stderr"), "wb") as f:
            f.write(proc_unpaper_err)
    with open(os.path.join(os.path.dirname(output_file_path), "unpaper-retcode"), "wb") as f:
        f.write(str(proc_unpaper.returncode))

    # Change path back and return
    return proc_unpaper.returncode
