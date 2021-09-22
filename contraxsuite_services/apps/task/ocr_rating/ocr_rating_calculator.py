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


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import os
import tempfile
import pandas

import lexnlp.extract.common.ocr_rating.ocr_rating_calculator as lexnlp_ocr_path
from lexnlp.extract.common.ocr_rating.ocr_rating_calculator import \
    QuadraticCosineSimilarityOcrRatingCalculator
from apps.common.file_storage import get_file_storage
from apps.common.singleton import Singleton


CUSTOM_LANG_STORAGE_FOLDER = 'ocr_rating_files'


class RatingCalculator(QuadraticCosineSimilarityOcrRatingCalculator):
    def get_rating(self, text: str, language: str) -> float:
        cs = super().get_cs(text, language)
        x = (cs - 0.5) * 2 * 5
        ocr_grade = round(max(0.0, x))
        return ocr_grade


@Singleton
class TextOCRRatingCalculator:
    def __init__(self):
        self.calc = RatingCalculator()

        fstor = get_file_storage()
        extra_language_paths = fstor.list(CUSTOM_LANG_STORAGE_FOLDER)
        for file_path in extra_language_paths:
            file_data = fstor.read(file_path)
            with tempfile.NamedTemporaryFile() as fw:
                fw.write(file_data)
                lang_df = pandas.read_pickle(fw.name)
                lang, _ = os.path.splitext(os.path.basename(file_path))
                self.calc.distribution_by_lang[lang] = lang_df
        # load default lang features
        self.calc.init_language_data(
            [os.path.join(os.path.dirname(lexnlp_ocr_path.__file__), './reference_vectors')])

    def calculate_rating(self, text: str, language: str) -> float:
        return self.calc.get_rating(text, language or '')
