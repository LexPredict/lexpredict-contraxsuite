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

import ast
from typing import Any
from collections.abc import Iterable

import asttokens

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.1.0/LICENSE"
__version__ = "2.1.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class PythonExpressionChecker:

    def __init__(self, code: str):
        self.code = code
        self.errors = []
        self.warnings = []
        self.st = None

    def test_expression(self):
        try:
            self.st = asttokens.ASTTokens(self.code, parse=True)  # ast.parse(self.code)
        except Exception as e:
            self.errors.append(f'Error executing expression: {e}')
            return
        if not self.st._tree or not self.st._tree.body:
            return
        self.test_correct_comparing(self.st._tree.body)

    def test_correct_comparing(self, node: Any = None) -> None:
        if not node:
            return
        if isinstance(node, Iterable):
            for item in node:
                self.test_correct_comparing(item)
            return

        if isinstance(node, ast.Expr):
            self.test_correct_comparing(node.value)
            return

        if isinstance(node, ast.BinOp):
            self.test_correct_comparing(node.left)
            self.test_correct_comparing(node.right)
            return

        if isinstance(node, ast.BoolOp):
            for val in node.values:
                self.test_correct_comparing(val)
            return

        if isinstance(node, ast.IfExp):
            self.test_correct_comparing(node.body)
            self.test_correct_comparing(node.test)
            self.test_correct_comparing(node.orelse)
            return

        if isinstance(node, ast.Compare):
            if isinstance(node.left, ast.Name):
                comparator = node.comparators[0]
                operation = node.ops[0]
                if isinstance(operation, (ast.Is, ast.IsNot)):
                    # Is or IsNot are allowed for NameConstant - None - only
                    if isinstance(comparator, ast.NameConstant) and comparator.value is None:
                        return
                    node_text = self.stringify_node(node)
                    self.errors.append(f'Checking "{node_text}" '
                                       'is unsafe, use "==" operator instead')
                    self.test_correct_comparing(comparator)

    def stringify_node(self, node: Any) -> str:
        if hasattr(node, 'first_token') and hasattr(node, 'last_token'):
            return self.code[node.first_token.startpos:node.last_token.endpos]

        if isinstance(node, ast.NameConstant):
            return str(node.value)
        if isinstance(node, ast.Str):
            return "'" + node.s.replace("'", "''") + "'"
        if isinstance(node, ast.Num):
            return str(node.n)
        if isinstance(node, ast.BinOp):
            left = self.stringify_node(node.left)
            right = self.stringify_node(node.right)
            op = self.stringify_operation(node.op)
            return f'{left} {op} {right}'

        return str(node)

    @staticmethod
    def stringify_operation(op: Any) -> str:
        if isinstance(op, ast.Add):
            return '+'
        if isinstance(op, ast.Sub):
            return '-'
        if isinstance(op, ast.Mult):
            return '*'
        if isinstance(op, (ast.Div, ast.FloorDiv)):
            return '/'
        return str(op)
