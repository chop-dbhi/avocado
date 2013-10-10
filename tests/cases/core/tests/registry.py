from django.test import TestCase
from avocado.core.loader import Registry, AlreadyRegistered

class RegistryTestCase(TestCase):
    def setUp(self):
        class A(object): pass
        class B(object): pass
        self.A = A
        self.B = B
        self.r = Registry(register_instance=False)

    def test_register(self):
        self.r.register(self.B)
        self.r.register(self.A)
        self.assertEqual(self.r.choices, [('A', 'A'), ('B', 'B')])

    def test_unregister(self):
        self.r.register(self.A)
        self.assertEqual(self.r.choices, [('A', 'A')])
        self.r.unregister(self.A)
        self.assertEqual(self.r.choices, [])

    def test_already(self):
        self.r.register(self.A)
        self.assertRaises(AlreadyRegistered, self.r.register, self.A)

    def test_default(self):
        class C(object): pass
        self.r.register(C, default=True)
        self.assertEqual(self.r['Default'], C)

        class D(object): pass
        self.r.register(D, default=True)
        self.assertEqual(self.r['Default'], D)
