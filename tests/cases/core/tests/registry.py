from django.test import TestCase
from avocado.core.loader import Registry, AlreadyRegistered


class A(object):
    pass


class B(object):
    pass


class C(object):
    pass


class D(object):
    pass


class RegistryTestCase(TestCase):
    def setUp(self):
        self.r = Registry(register_instance=False)

    def test_register(self):
        self.r.register(B)
        self.r.register(A)
        self.assertEqual(self.r.choices, [('A', 'A'), ('B', 'B')])

    def test_unregister(self):
        self.r.register(A)
        self.assertEqual(self.r.choices, [('A', 'A')])
        self.r.unregister(A)
        self.assertEqual(self.r.choices, [])

    def test_already(self):
        self.r.register(A)
        self.assertRaises(AlreadyRegistered, self.r.register, A)

    def test_default(self):
        self.r.register(C, default=True)
        self.assertEqual(self.r['Default'], C)

        self.r.register(D, default=True)
        self.assertEqual(self.r['Default'], D)

    def test_decorator(self):
        @self.r.register
        class E(object):
            pass

        self.assertEqual(self.r.choices, [('E', 'E')])

    def test_decorator_arguments(self):
        @self.r.register('F Class', default=True)
        class F(object):
            pass

        self.assertEqual(self.r.choices, [('F Class', 'F Class')])
        self.assertEqual(self.r.default, F)
