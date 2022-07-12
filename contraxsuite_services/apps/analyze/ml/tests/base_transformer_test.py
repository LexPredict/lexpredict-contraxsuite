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

from django.test import TestCase
import shutil
import pathlib
import os

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class BaseTransformerTest(TestCase):
    model_reserve_path = ''

    @classmethod
    def setUpClass(cls):
        model_path = cls._get_model_path()
        model_reserve_path = model_path + '.old'
        cls.model_reserve_path = ''
        try:
            # store the original model file
            shutil.move(model_path, model_reserve_path)
            cls.model_reserve_path = model_reserve_path
        except Exception as e:
            pass

    @classmethod
    def tearDownClass(cls):
        if not cls.model_reserve_path or not os.path.isfile(cls.model_reserve_path):
            return

        model_path = cls._get_model_path()
        try:
            os.remove(model_path)
        except:
            pass
        try:
            # restore the original model file
            shutil.move(cls.model_reserve_path, model_path)
        except Exception as e:
            pass
        cls.model_reserve_path = ''

    @classmethod
    def _get_model_path(cls) -> str:
        return os.path.join(
            pathlib.Path(__file__).parent.absolute(),
            'test_data',
            'models/en/transformer/document/document_doc2vec_dm_1_vector_100_window_10/model.pickle')
