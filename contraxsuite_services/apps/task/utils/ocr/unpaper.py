# -*- coding: utf-8 -*-
__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0/LICENSE.pdf"
__version__ = "1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@lexpredict.com"

# Standard imports
import os
import subprocess

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
