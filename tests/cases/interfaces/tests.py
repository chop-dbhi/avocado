from django.test import TestCase
from avocado import interfaces


class InterfaceLoaderTestCase(TestCase):
    def test_get_interfaces(self):
        self.assertEqual(len(interfaces.get_interfaces()), 1)

    
