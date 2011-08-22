from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured
from avocado.utils.loader import Registry, AlreadyRegistered

__all__ = ('RegistryTestCase',)

class RegistryTestCase(TestCase):
    def setUp(self):
        class A(object): pass
        class B(object): pass
        self.A = A
        self.B = B
        self.r = Registry(default=A)

    def test_register(self):
        self.r.register(self.B)
        self.assertEqual(self.r.choices, [(self.A, 'A'), (self.B, 'B')])

    def test_unregister(self):
        self.r.unregister(self.A)
        self.assertEqual(self.r.choices, [])

    def test_already(self):
        self.assertRaises(AlreadyRegistered, self.r.register, self.A)

    def test_default(self):
        class C(object): pass
        C.default = True
        self.assertRaises(ImproperlyConfigured, self.r.register, C)

