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

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


from apps.notifications.models import WebNotificationStorage


class TestWebNotificationStorage(TestCase):
    def test_singleton(self) -> None:
        first_storage = WebNotificationStorage()
        second_storage = WebNotificationStorage()
        self.assertEqual(id(first_storage), id(second_storage))

    def test_min_add_extract(self) -> None:
        storage = WebNotificationStorage()
        storage.add('1')
        storage.add('3')
        self.assertEqual(storage.extract(), ['1', '3'])

    def test_max_add_extract(self) -> None:
        storage = WebNotificationStorage()
        storage.add('1')
        for i in range(25):
            storage.add('3')
        self.assertEqual(len(storage.extract()), storage.NOTIFICATION_BATCH_SIZE)
        for i in range(int(25/storage.NOTIFICATION_BATCH_SIZE)+1):
            storage.extract()
