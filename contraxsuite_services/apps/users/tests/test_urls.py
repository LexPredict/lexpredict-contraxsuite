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
__copyright__ = "Copyright 2015-2018, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.7/LICENSE"
__version__ = "1.1.7"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

from django.core.urlresolvers import reverse, resolve

from test_plus.test import TestCase


class TestUserURLs(TestCase):
    """Test URL patterns for users app."""

    def setUp(self):
        self.user = self.make_user()

    def test_list_reverse(self):
        """users:list should reverse to /users/."""
        self.assertEqual(reverse('users:list'), '/users/')

    def test_list_resolve(self):
        """/users/ should resolve to users:list."""
        self.assertEqual(resolve('/users/').view_name, 'users:list')

    def test_redirect_reverse(self):
        """users:redirect should reverse to /users/~redirect/."""
        self.assertEqual(reverse('users:redirect'), '/users/~redirect/')

    def test_redirect_resolve(self):
        """/users/~redirect/ should resolve to users:redirect."""
        self.assertEqual(
            resolve('/users/~redirect/').view_name,
            'users:redirect'
        )

    def test_detail_reverse(self):
        """users:detail should reverse to /users/testuser/."""
        self.assertEqual(
            reverse('users:detail', kwargs={'username': 'testuser'}),
            '/users/testuser/'
        )

    def test_detail_resolve(self):
        """/users/testuser/ should resolve to users:detail."""
        self.assertEqual(resolve('/users/testuser/').view_name, 'users:detail')

    def test_update_reverse(self):
        """users:update should reverse to /users/~update/."""
        self.assertEqual(reverse('users:update'), '/users/~update/')

    def test_update_resolve(self):
        """/users/~update/ should resolve to users:update."""
        self.assertEqual(
            resolve('/users/~update/').view_name,
            'users:update'
        )
