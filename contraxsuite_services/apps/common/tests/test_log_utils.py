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

from unittest import TestCase
from apps.common.log_utils import render_exception

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestLogUtils(TestCase):

    def f_cause1(self):
        print(int(self))

    def f_cause2(self):
        try:
            self.f_cause1()
        except Exception as ve:
            raise RuntimeError('runtime_cause2\nnew line') from ve

    def f_cause3(self, raise_in_context=False):
        try:
            self.f_cause2()
        except RuntimeError as re:
            if raise_in_context:
                raise ValueError('exception_cause3\nnew line')
            raise ValueError('exception_cause3\nnew line') from re

    def test_render_exception(self):
        try:
            self.f_cause3()
            self.assertTrue(False)
        except ValueError as e:
            actual = render_exception(e)
            print(actual)
            self.assertTrue(True)


TestLogUtils().test_render_exception()
