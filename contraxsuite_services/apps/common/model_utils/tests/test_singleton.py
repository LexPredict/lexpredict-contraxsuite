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

import time
from threading import Lock, Thread
from typing import List

from apps.common.singleton import Singleton
from tests.django_test_case import DjangoTestCase

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2020, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/1.8.0/LICENSE"
__version__ = "1.8.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


class MyClass1:
    def __init__(self) -> None:
        super().__init__()
        self.val = 'a'


@Singleton
class MyClass2(MyClass1):
    pass


@Singleton
class MyClass3(MyClass1):
    pass


my_class4_init_lock = Lock()
main_thread_lock = Lock()


@Singleton
class MyClass4:
    def __init__(self, val) -> None:
        super().__init__()
        with my_class4_init_lock:
            self.val = val
            print(f'MyClass4(val={val})')


class TestSingleton(DjangoTestCase):
    def test_singleton(self):
        o1 = MyClass1()
        o1.val = 1

        o2 = MyClass1()
        o2.val = 2

        self.assertEqual(o1.val, 1, 'Non-singleton parent classes should have separate internal states.')
        self.assertEqual(o2.val, 2, 'Non-singleton parent classes should have separate internal states.')

        p1 = MyClass2()
        p1.val = 1

        p2 = MyClass2()
        p2.val = 2

        p3 = MyClass3()
        p3.val = 3

        self.assertEqual(p1.val, 2, 'Singleton class constructor should return the same object for all instantiations.')
        self.assertEqual(p2.val, 2, 'Singleton class constructor should return the same object for all instantiations.')
        self.assertEqual(p3.val, 3, 'Singleton class constructor should return the same object for all instantiations.')

    def manual_test_thread_safety(self):
        # TODO: fix test for predictable output
        o1 = []  # type: List[MyClass4]
        o2 = []  # type: List[MyClass4]

        f1_lock = Lock()
        f2_lock = Lock()

        def f1():
            print('f1: paused by f1_lock...')
            with f1_lock:
                print('f1: continues...')
                o1.append(MyClass4(1))
            main_thread_lock.release()
            try:
                main_thread_lock.release()
            except RuntimeError:
                pass

        def f2():
            print('f2: paused by f2_lock...')
            with f2_lock:
                o2.append(MyClass4(2))
            try:
                main_thread_lock.release()
            except RuntimeError:
                pass

        my_class4_init_lock.acquire()
        f1_lock.acquire()
        f2_lock.acquire()
        main_thread_lock.acquire()

        th2 = Thread(target=f2)
        th2.start()
        th1 = Thread(target=f1)
        time.sleep(0.3)
        th1.start()

        print('Unlocking f1: it should try to init MyClass4(val=1) and hang on my_class4_init_lock inside the __init__')
        f1_lock.release()
        print('Unlocking f2: it should hang on the singleton lock preventing MyClass4 from being init with val=2')
        f2_lock.release()

        print('Unlocking MyClass4.__init__(): f1 should finish first, next f2')
        my_class4_init_lock.release()

        with main_thread_lock:
            o3 = MyClass4(val=3)

        print(f'Finally singleton has val = {o3.val}')

        self.assertEqual(1, o3.val, 'It is a singleton, it should have the state as it was defined on the first init')
