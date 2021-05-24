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
from apps.document.pdf_coordinates.text_coord_map import TextCoordMap, Dir

# -*- coding: utf-8 -*-


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.0.0/LICENSE"
__version__ = "2.0.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


def test_extends_rect_right1():
    s = (-3, 0.5, 0.5, 0.5)
    o = (-2.5, 0.5, 0.5, 0.5)
    so_expected = (Dir.horizontal, (-3, 0.5, 1, 0.5))
    so_actual = TextCoordMap.extend_rect(None, s, o)
    print(so_actual)
    assert so_actual == so_expected


def test_extends_rect_left1():
    s = (-3, 0.5, 0.5, 0.5)
    o = (-2.5, 0.5, 0.5, 0.5)
    so_expected = (Dir.horizontal, (-3, 0.5, 1, 0.5))
    so_actual = TextCoordMap.extend_rect(None, o, s)
    print(so_actual)
    assert so_actual == so_expected


def test_extends_rect_h1():
    s = (-3, 0.5, 0.5, 0.5)
    o = (-3.9, 0.5, 0.5, 0.5)
    so_expected = (Dir.horizontal, (-3.9, 0.5, 1.4, 0.5))
    so_actual = TextCoordMap.extend_rect(None, o, s)
    print(so_actual)
    assert so_actual == so_expected


def test_extends_rect_h2():
    s = (-3, 0.5, 0.5, 0.5)
    o = (-3.9, 0.8, 0.5, 0.5)  # another line
    so_expected = None
    so_actual = TextCoordMap.extend_rect(None, o, s)
    print(so_actual)
    assert so_actual == so_expected


def test_extends_rect_v1():
    s = (0.5, -3, 0.5, 0.5)
    o = (0.5, -2.5, 0.5, 0.5)
    so_expected = (Dir.vertical, (0.5, -3, 0.5, 1))
    so_actual = TextCoordMap.extend_rect(None, o, s)
    print(so_actual)
    assert so_actual == so_expected


def test_extends_rect_v2():
    so = (0.5, -2.5, 0.5, 1)
    n = (0.5, -1.5, 0.5, 0.5)
    son_expected = (Dir.vertical, (0.5, -2.5, 0.5, 1.5))
    son_actual = TextCoordMap.extend_rect(Dir.vertical, so, n)
    print(son_actual)
    assert son_actual == son_expected


def test_extends_rect_v3():
    on = (0.5, -2, 0.5, 1)
    s = (0.5, -2.5, 0.5, 0.5)
    son_expected = (Dir.vertical, (0.5, -2.5, 0.5, 1.5))
    son_actual = TextCoordMap.extend_rect(Dir.vertical, on, s)
    print(son_actual)
    assert son_actual == son_expected


def test_extends_rect_v4():
    on = (0.5, -2, 0.5, 1)
    v = (1, -2, 0.5, 0.5)
    son_expected = None, None
    son_actual = TextCoordMap.extend_rect(Dir.vertical, on, v)
    print(son_actual)
    assert son_actual == son_expected
