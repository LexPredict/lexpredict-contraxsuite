from threading import Lock, Thread
from typing import List

from apps.common.singleton import Singleton
from tests.django_test_case import DjangoTestCase


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

    def test_thread_safety(self):
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
