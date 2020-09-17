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

from apps.common.expressions import PythonExpressionChecker
from tests.django_test_case import *

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.7.0/LICENSE"
__version__ = "1.7.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class TestExpressions(TestCase):

    def test_warn_is_str(self):
        code = "temperature is '10'"
        checker = PythonExpressionChecker(code)
        checker.test_expression()
        self.assertEqual(1, len(checker.warnings))

        code = "temperature == '10'"
        checker = PythonExpressionChecker(code)
        checker.test_expression()
        self.assertEqual(0, len(checker.warnings))

    def test_warn_is_diff_types(self):
        code = "temperature is True"
        checker = PythonExpressionChecker(code)
        checker.test_expression()
        self.assertEqual(1, len(checker.warnings))
        self.assertTrue("temperature is True" in checker.warnings[0])

        code = "temperature is 10.2"
        checker = PythonExpressionChecker(code)
        checker.test_expression()
        self.assertEqual(1, len(checker.warnings))
        self.assertTrue("temperature is 10.2" in checker.warnings[0])

    def test_warn_is_binop(self):
        code = "temperature is 5 - 2"
        checker = PythonExpressionChecker(code)
        checker.test_expression()
        self.assertEqual(1, len(checker.warnings))
        self.assertTrue("temperature is 5 - 2" in checker.warnings[0])

        code = "temperature is 5 / 2"
        checker = PythonExpressionChecker(code)
        checker.test_expression()
        self.assertTrue("temperature is 5 / 2" in checker.warnings[0])

    def test_warn_is_expr(self):
        code = "temperature is (5 - 2) * 2"
        checker = PythonExpressionChecker(code)
        checker.test_expression()
        self.assertEqual(1, len(checker.warnings))
        self.assertTrue("temperature is (5 - 2) * 2" in checker.warnings[0])

    def test_big_safe_expr(self):
        code = "(['26 One'] if k_eight is not None and 'Blah' in k_eight else []) " +\
            "+ (['26 Two'] if k_eight is not None and 'Blah-Blah' in k_eight " +\
            "else []) + (['26 Three'] if k_eight is not None and " +\
            "'Blah-Blah-Blah' in k_eight else [])".strip()
        checker = PythonExpressionChecker(code)
        checker.test_expression()
        self.assertEqual(0, len(checker.errors))
        self.assertEqual(0, len(checker.warnings))

    def test_ternary(self):
        code = "1 if k_nine is '' else 0"
        checker = PythonExpressionChecker(code)
        checker.test_expression()
        self.assertEqual(0, len(checker.errors))
        self.assertEqual(1, len(checker.warnings))

    def test_avg_len_with_warns(self):
        code = "k_nine if k_nine is '' else float(k_19) / 234.6 if k_19 else None"
        checker = PythonExpressionChecker(code)
        checker.test_expression()
        self.assertEqual(0, len(checker.errors))
        self.assertEqual(1, len(checker.warnings))

    def test_complex(self):
        code = 'k_one - k_14 if k_one is \'1\' and k_14 else None'
        checker = PythonExpressionChecker(code)
        checker.test_expression()
        self.assertEqual(0, len(checker.errors))
        self.assertEqual(1, len(checker.warnings))
