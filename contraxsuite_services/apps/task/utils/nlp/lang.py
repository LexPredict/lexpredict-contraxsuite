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

# Tika and langid imports
import langid.langid
import tika.language

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.2.3/LICENSE"
__version__ = "1.2.3"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


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

    try:
        return lang_identifier.classify(input_buffer)[0]
    except:
        return ''


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


def get_language(input_buffer, get_parser=False, encoding="utf-8"):
    lang = parser = None

    # try to extract using LANGID
    try:
        lang = get_language_langid(input_buffer, encoding=encoding)
        parser = 'langid'
    except:
        pass

    # try to extract using TIKA
    if not lang:
        try:
            lang = get_language_tika(input_buffer, encoding=encoding)
            parser = 'tika'
        except:
            pass

    if not lang:
        lang = parser = None

    if get_parser:
        return lang, parser

    return lang
