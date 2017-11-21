# -*- coding: utf-8 -*-
# Standard imports
import os
import subprocess

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.3/LICENSE"
__version__ = "1.0.3"
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
