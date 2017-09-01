# -*- coding: utf-8 -*-
# Standard imports
import os
import subprocess

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.1/LICENSE"
__version__ = "1.0.1"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

# TODO: Allow configuration-based poppler path.
POPPLER_UTILS_PATH = "/usr/bin/"


def export_pdf_to_ppm(input_file_path, working_path="/tmp", pdftoppm_dpi=200):
    """
    Export a PDF to PPM files at a given DPI and directory.
    :param input_file_path: path to input PDF file
    :param working_path: path to working directory to export files
    :param pdftoppm_dpi: DPI to export at
    :return: return code
    """
    # Change path
    original_path = os.getcwd()
    os.chdir(working_path)

    # Setup command arguments and execute
    args_pdftoppm = [os.path.join(POPPLER_UTILS_PATH, "pdftoppm"),
                     "-rx", str(pdftoppm_dpi), "-ry", str(pdftoppm_dpi),
                     input_file_path, "page"]
    proc_pdftoppm = subprocess.Popen(args_pdftoppm, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc_pdftoppm_out, proc_pdftoppm_err = proc_pdftoppm.communicate()
    proc_pdftoppm.wait()

    # Write stdout/err/retcode
    if proc_pdftoppm_out:
        with open(os.path.join(working_path, "pdftoppm-stdout"), "wb") as f:
            f.write(proc_pdftoppm_out)
    if proc_pdftoppm_err:
        with open(os.path.join(working_path, "pdftoppm-stderr"), "wb") as f:
            f.write(proc_pdftoppm_err)
    with open(os.path.join(working_path, "pdftoppm-retcode"), "w") as f:
        f.write(str(proc_pdftoppm.returncode))

    # Change path back and return
    os.chdir(original_path)
    return proc_pdftoppm.returncode


def export_pdf_to_text(input_file_path, output_file_path, encoding="UTF-8"):
    """
    Export a PDF to text file.
    :param input_file_path: path to input PDF file
    :param output_file_path: path to output text file
    :param encoding: character encoding
    :return: return code
    """
    # Setup command arguments and execute
    args_pdftotext = [os.path.join(POPPLER_UTILS_PATH, "pdftotext"),
                      "-enc", encoding,
                      input_file_path, output_file_path]
    proc_pdftotext = subprocess.Popen(args_pdftotext, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
    proc_pdftotext_out, proc_pdftotext_err = proc_pdftotext.communicate()
    proc_pdftotext.wait()

    # Write stdout/err/retcode
    if proc_pdftotext_out:
        with open(os.path.join(os.path.dirname(output_file_path), "pdftotext-stdout"), "wb") as f:
            f.write(proc_pdftotext_out)
    if proc_pdftotext_err:
        with open(os.path.join(os.path.dirname(output_file_path), "pdftotext-stderr"), "wb") as f:
            f.write(proc_pdftotext_err)
    with open(os.path.join(os.path.dirname(output_file_path), "pdftotext-retcode"), "w") as f:
        f.write(str(proc_pdftotext.returncode))

    # Return
    return proc_pdftotext.returncode


def export_pdf_to_html(input_file_path, output_file_path, encoding="UTF-8"):
    """
    Export a PDF to HTML file.
    :param input_file_path: path to input PDF file
    :param output_file_path: path to output HTML file
    :param encoding: character encoding
    :return: return code
    """
    # Setup command arguments and execute
    args_pdftohtml = [os.path.join(POPPLER_UTILS_PATH, "pdftohtml"),
                      "-enc", encoding,
                      "-noframes", "-s", "-xml",
                      input_file_path, output_file_path]
    proc_pdftohtml = subprocess.Popen(args_pdftohtml, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
    proc_pdftohtml_out, proc_pdftohtml_err = proc_pdftohtml.communicate()
    proc_pdftohtml.wait()

    # Write stdout/err/retcode
    if proc_pdftohtml_out:
        with open(os.path.join(os.path.basename(output_file_path), "pdftohtml-stdout"), "wb") as f:
            f.write(proc_pdftohtml_out)
    if proc_pdftohtml_err:
        with open(os.path.join(os.path.basename(output_file_path), "pdftohtml-stderr"), "wb") as f:
            f.write(proc_pdftohtml_err)
    with open(os.path.join(os.path.basename(output_file_path), "pdftohtml-retcode"), "w") as f:
        f.write(str(proc_pdftohtml.returncode))

    # Return
    return proc_pdftohtml.returncode
