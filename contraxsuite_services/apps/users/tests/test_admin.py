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
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.1.2/LICENSE"
__version__ = "1.1.2"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"

from test_plus.test import TestCase

from ..admin import MyUserCreationForm


class TestMyUserCreationForm(TestCase):

    def setUp(self):
        self.user = self.make_user('notalamode', 'notalamodespassword')

    def test_clean_username_success(self):
        # Instantiate the form with a new username
        form = MyUserCreationForm({
            'username': 'alamode',
            'password1': '7jefB#f@Cc7YJB]2v',
            'password2': '7jefB#f@Cc7YJB]2v',
        })
        # Run is_valid() to trigger the validation
        valid = form.is_valid()
        self.assertTrue(valid)

        # Run the actual clean_username method
        username = form.clean_username()
        self.assertEqual('alamode', username)

    def test_clean_username_false(self):
        # Instantiate the form with the same username as self.user
        form = MyUserCreationForm({
            'username': self.user.username,
            'password1': 'notalamodespassword',
            'password2': 'notalamodespassword',
        })
        # Run is_valid() to trigger the validation, which is going to fail
        # because the username is already taken
        valid = form.is_valid()
        self.assertFalse(valid)

        # The form.errors dict should contain a single error called 'username'
        self.assertTrue(len(form.errors) == 1)
        self.assertTrue('username' in form.errors)
