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


from tests.django_test_case import *
from django.test import TestCase
from apps.common.utils import Map, cap_words, clean_html_tags


class TestMap(TestCase):
    def test_map(self):
        m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
        self.assertEqual('Eduardo', m.first_name)
        self.assertEqual('Pool', m.last_name)
        self.assertEqual(24, m.age)
        self.assertEqual(['Soccer'], m.sports)

    def test_cap_words(self):
        self.assertEqual(
            'Presently My Soul Grew Stronger; Hesitating Then No Longer, ' +
            '“Sir,” Said I, “or Madam, Truly Your Forgiveness I Implore',
            cap_words('''Presently my soul grew stronger; 
            hesitating then no longer, “Sir,” said I, “or Madam, 
            truly your forgiveness I implore
            '''))

    def test_clean_html_tags(self):
        self.assertEqual(
            'Some  semibold text',
            clean_html_tags('Some <b> semibold</b> text'))

        self.assertEqual(
            'Some  semibold and italic text',
            clean_html_tags('Some <b> semibold <i>and italic</i></b> text'))

        self.assertEqual(
            'This text contains \ncontextual hyperlink  and some italic text.',
            clean_html_tags('This text contains <a href="#" alt="some">\n<b>contextual</b> ' +
                            'hyperlink </a> and some <italic>italic</italic> text.'))
