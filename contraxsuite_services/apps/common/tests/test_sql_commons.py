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
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import regex as re
from unittest import TestCase

from apps.common.sql_commons import escape_column_name, SQLClause, join_clauses, SQLInsertClause


class TestSqlCommons(TestCase):
    def test_escape_column_name(self):
        self.assertEqual('money_amount', escape_column_name('MoneyAmount'))
        self.assertEqual('init', escape_column_name('__init_'))

    def test_join_clauses(self):
        clauses = [
            SQLClause('select name, "order" from stock_product'),
            SQLClause('where code in (%s)', [['alpha', 'bravo', 'charlie']]),
            SQLClause(' group by name desc;')
        ]
        clause = join_clauses(' ', clauses)
        self.assertIsNotNone(clause)
        self.assertEqual('select name, "order" from stock_product where code in (%s)  group by name desc;',
                         clause.sql)
        self.assertEqual(1, len(clause.params))

        clause = join_clauses(' ', clauses, True)
        self.assertIsNotNone(clause)
        self.assertEqual('(select name, "order" from stock_product) (where code in (%s)) ( group by name desc;)',
                         clause.sql)

    def test_sql_insert(self):
        clauses = [SQLInsertClause(
            '"currency", "raw_amount"', [], '%s, %s', ['EUR', 10050]),
            SQLInsertClause(
                '"duration", "units"', [], '%s, %s', [5, 's'])
        ]
        joined = SQLInsertClause.join(clauses)

        self.assertIsNotNone(joined)
        self.assertEqual('currencyraw_amountdurationunits',
                         re.sub(r'[\s,"]+', '', joined[0].sql))
        self.assertEqual('%s%s%s%s', re.sub(r'[\s,]+', '', joined[1].sql))
        self.assertIsNotNone(joined[1].params)
        self.assertEqual(4, len(joined[1].params))
