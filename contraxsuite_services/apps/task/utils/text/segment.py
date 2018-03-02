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
import string

# NLTK imports
import nltk.tokenize
import nltk.tokenize.punkt

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0.5/LICENSE"
__version__ = "1.0.6"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def segment_paragraphs(input_buffer):
    """
    Segment a text buffer into paragraphs.
    :param input_buffer:
    :return:
    """
    # Clean up text
    LAST_LINE_EMPTY = False
    CURRENT_LINE_EMPTY = False
    # START_COLON = False
    TERMINAL_COLON = False
    LAST_LINE_COLON = False
    TERMINAL_PERIOD = False
    TERMINAL_SEMICOLON = False
    # START_SECTION = False
    # START_NUMBERING = False

    line_flags = []
    current_paragraph = str()
    paragraphs = []

    for line in input_buffer.splitlines():
        # Get re-used fields
        tokens = line.strip().split()

        # Set flags
        if line.strip().endswith(":"):
            TERMINAL_COLON = True

        if len(tokens) > 0 and tokens[0].endswith(":"):
            pass
            # START_COLON = True

        if line.strip().endswith(";"):
            TERMINAL_SEMICOLON = True

        if line.strip().endswith("."):
            TERMINAL_PERIOD = True

        if len(line.strip()) == 0:
            CURRENT_LINE_EMPTY = True

        if line.strip().lower().startswith("section"):
            pass
            # START_SECTION = True

        if all([c in string.digits for c in line.strip().lower().replace("page", "")]):
            pass
            # START_NUMBERING = True

        # Process flags
        if CURRENT_LINE_EMPTY and not LAST_LINE_COLON:
            if len(current_paragraph.strip()) > 0:
                paragraphs.append(current_paragraph.strip())
            current_paragraph = line.strip()
        elif TERMINAL_COLON:
            current_paragraph += " " + line.strip()
        else:
            current_paragraph += " " + line.strip()

        # Append flags
        line_flags.append((TERMINAL_COLON, TERMINAL_SEMICOLON, TERMINAL_PERIOD,
                           LAST_LINE_EMPTY, CURRENT_LINE_EMPTY))

        # Update flags
        LAST_LINE_COLON = TERMINAL_COLON
        TERMINAL_COLON = False

        TERMINAL_PERIOD = False

        TERMINAL_SEMICOLON = False

        LAST_LINE_EMPTY = CURRENT_LINE_EMPTY
        CURRENT_LINE_EMPTY = False

    # Append final paragraph
    paragraphs.append(current_paragraph.strip())

    return paragraphs


def segment_sentences(input_buffer):
    """
    Segment a buffer into sentences.
    :param input_buffer: input buffer
    :return:
    """
    # Setup unsupervised sentence tokenizer
    # TODO: Allow configurable sentence tokenizer.
    sent_tokenizer = nltk.tokenize.punkt.PunktSentenceTokenizer(input_buffer)
    sentences = []

    # Iterate over paragraphs
    for paragraph in segment_paragraphs(input_buffer):
        sentences.extend(sent_tokenizer.tokenize(paragraph))

    return sentences
