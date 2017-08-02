# -*- coding: utf-8 -*-
__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0/LICENSE.pdf"
__version__ = "1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@lexpredict.com"

# Tika imports
from tika import parser


def tika2text(file_path):
    """
    https://github.com/chrismattmann/tika-python

    Firstly run tika server
    To parse buffer:
    parsed = parser.from_buffer(buffer)

    parsed has ['metadata'] with useful info
    """

    # Call via python-tika API
    parsed = parser.from_file(file_path)
    return parsed['content']
