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

import regex as re

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.5.0/LICENSE"
__version__ = "1.5.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class HeadingHeuristics:
    """
    This class helps to decide which of the two strings
    looks more like a section heading (title)
    """

    # detect section numbering in possible heading
    HEADING_DETECTOR_RE = re.compile(r"(^[IVXC][IVXC\.]*\s)|(^\d[\d\.]*\s)")
    # string longer than MAX_LEN is hardly a heading
    MAX_LEN = 150
    # string longer than MAX_PLAUS_LEN still can be a heading
    MAX_PLAUS_LEN = 100
    # string shorter than MIN_PLAUS_LEN is hardly a heading
    MIN_LEN = 4
    # old title variant's preference
    OLD_PREFERENCE = 7
    # weights in total score:
    # contains title; length is optimal; longer than another; capitalized; starts with numbering; contains linebreak;
    SCORE_WEIGHTS = [10, 10, 5, 5, 10, -20]

    @classmethod
    def get_better_title(cls, existing_title: str, possible_title: str):
        score_new = cls.get_title_score(existing_title, possible_title)
        if score_new < 0:
            return existing_title
        score_old = cls.get_title_score(possible_title, existing_title) + cls.OLD_PREFERENCE
        return existing_title if score_old > score_new else possible_title

    @classmethod
    def get_title_score(cls, existing_title: str, possible_title: str):
        if len(possible_title) > cls.MAX_LEN:
            return -1000
        if len(possible_title) < cls.MIN_LEN:
            return -1000

        # check if possible_title is a good replacement for section title already found
        contains_title = existing_title.replace(' ', '') in possible_title.replace(' ', '')
        optimal_len = len(possible_title) < cls.MAX_PLAUS_LEN
        capitalized = possible_title.upper() == possible_title
        longer_than = cls.MAX_PLAUS_LEN > len(possible_title) > len(existing_title)
        contains_linebreak = '\n' in possible_title

        starts_with_numbering = True \
            if cls.HEADING_DETECTOR_RE.search(possible_title) else False

        ws = cls.SCORE_WEIGHTS
        score = contains_title * ws[0] + optimal_len * ws[1] +\
            longer_than * ws[2] + capitalized * ws[3] +\
            starts_with_numbering * ws[4] + contains_linebreak * ws[5]
        return score
