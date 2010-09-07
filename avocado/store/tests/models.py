from django.test import TestCase

from avocado.store.models import Scope, Perspective

__all__ = ('ScopeTestCase',)

class ScopeTestCase(TestCase):
    def test_pickling(self):
        scope = Scope()
        node = {
            'type': 'AND',
            'children': [{
                'id': 5,
                'operator': 'exact',
                'value': 10
            }, {
                'id': 3,
                'operator': 'exact',
                'value': True            
            }]
        }
        scope.write(node)
        scope.save()
        self.assertEqual(node, scope.read())