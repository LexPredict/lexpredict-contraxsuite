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
# NLTK imports
import nltk

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.6/LICENSE"
__version__ = "1.1.6"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def get_character_ngram_distribution(input_buffer, n=1, encoding="utf-8"):
    """
    Get distribution of character ngrams from input_buffer.
    :param input_buffer: input buffer
    :param n: n value, number of consecutive items
    :param encoding: default encoding
    """
    # Ensure we have a decoded string
    if isinstance(input_buffer, bytes):
        input_buffer = input_buffer.decode(encoding)

    # Convert to character ngrams
    ngrams = list(nltk.ngrams(input_buffer, n=n))
    return dict([(g, ngrams.count(g)) for g in set(ngrams)])


def get_word_ngram_distribution(input_buffer, n=1, encoding="utf-8",
                                tokenize_method=nltk.word_tokenize):
    """
    Get distribution of word n-grams (shingles) from input_buffer.
    :param input_buffer: input buffer
    :param n: n value, number of consecutive items
    :param encoding: default encoding
    :param tokenize_method: method called to tokenize input_buffer into words
    """
    # Ensure we have a decoded string
    if isinstance(input_buffer, bytes):
        input_buffer = input_buffer.decode(encoding)

    # Convert to character ngrams
    ngrams = list(nltk.ngrams(tokenize_method(input_buffer), n=n))
    return dict([(g, ngrams.count(g)) for g in set(ngrams)])


def get_word_skipgram_distribution(input_buffer, n=2, k=2, encoding="utf-8",
                                   tokenize_method=nltk.word_tokenize):
    """
    Get distribution of skipgrams with given n and k values from input_buffer.
    :param input_buffer:
    :param n:
    :param k:
    :param encoding:
    :param tokenize_method:
    :return:
    """
    # Ensure we have a decoded string
    if isinstance(input_buffer, bytes):
        input_buffer = input_buffer.decode(encoding)

    ngrams = nltk.ngrams(tokenize_method(input_buffer), n=n)
    return nltk.util.skipgrams(ngrams, n, k)
