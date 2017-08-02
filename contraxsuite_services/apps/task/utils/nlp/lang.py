# -*- coding: utf-8 -*-
__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2017, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.0/LICENSE.pdf"
__version__ = "1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@lexpredict.com"

# Tika and langid imports
import langid.langid
import tika.language

# Static identifier
lang_identifier = langid.langid.LanguageIdentifier.from_modelstring(
    langid.langid.model, norm_probs=True)


def get_language_langid(input_buffer, encoding="utf-8"):
    """
    Get most likely language and probability.
    :param input_buffer: input buffer
    :param encoding: default encoding for bytes
    :return: tuple with (lang, probability)
    """
    # Ensure we have a decoded string
    if isinstance(input_buffer, bytes):
        input_buffer = input_buffer.decode(encoding)

    return lang_identifier.classify(input_buffer)


def get_language_tika(input_buffer, encoding="utf-8"):
    """
    Get most likely language.
    :param input_buffer: input buffer
    :param encoding: default encoding for bytes
    :return: language
    """
    # Ensure we have a decoded string
    if isinstance(input_buffer, bytes):
        input_buffer = input_buffer.decode(encoding)

    return tika.language.from_buffer(input_buffer)
