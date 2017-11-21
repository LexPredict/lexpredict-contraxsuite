# -*- coding: utf-8 -*-
# Tika imports
from tika import parser

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.3/LICENSE"
__version__ = "1.0.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


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
