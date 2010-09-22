from django.test import TestCase
from django.contrib.auth.models import User

from avocado.store.models import Scope, Perspective, Report

__all__ = ('ScopeTestCase', 'PerspectiveTestCase', 'ReportTestCase')

class ScopeTestCase(TestCase):
    fixtures = ['test_data.yaml']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.context = Scope()

    def test_is_valid(self):
        self.assertTrue(self.context.is_valid({}))
        self.assertFalse(self.context.is_valid([]))

        class dict2(dict):
            pass

        self.assertTrue(self.context.is_valid(dict2()))

    def test_has_permission(self):
        self.assertTrue(self.context.has_permission())
        self.assertTrue(self.context.has_permission(user=self.user))

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

        self.assertTrue(self.context.has_permission(node))
        self.assertTrue(self.context.has_permission(node, self.user))

        node['children'][0]['id'] = 1

        self.assertFalse(self.context.has_permission(node))
        self.assertTrue(self.context.has_permission(node, self.user))

        node = {}

        self.assertTrue(self.context.has_permission(node))
        self.assertTrue(self.context.has_permission(node, self.user))

        node = {
            'id': 3,
            'operator': 'exact',
            'value': True
        }

        self.assertTrue(self.context.has_permission(node))
        self.assertTrue(self.context.has_permission(node, self.user))

class PerspectiveTestCase(TestCase):
    fixtures = ['test_data.yaml']

    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.context = Perspective()

    def test_is_valid(self):
        self.assertTrue(self.context.is_valid({}))
        self.assertFalse(self.context.is_valid([]))

        class dict2(dict):
            pass

        self.assertTrue(self.context.is_valid(dict2()))

    def test_has_permission(self):
        self.assertTrue(self.context.has_permission())
        self.assertTrue(self.context.has_permission(user=self.user))

        node = {}

        self.assertTrue(self.context.has_permission(node))
        self.assertTrue(self.context.has_permission(node, self.user))

        node = {'columns': [1]}

        self.assertFalse(self.context.has_permission(node))
        self.assertFalse(self.context.has_permission(node, self.user))

        node = {'ordering': [(1, 'desc')]}

        self.assertFalse(self.context.has_permission(node))
        self.assertFalse(self.context.has_permission(node, self.user))


class Object(object):
    pass


class ReportTestCase(TestCase):
    fixtures = ['test_data.yaml']

    def setUp(self):
        self.user = User.objects.get(id=1)
        self.request = Object()
        self.request.user = self.user
        self.request.session = {
            Report.REPORT_CACHE_KEY: {}
        }

        self.report = Report()
        self.report.scope = Scope()
        self.report.perspective = Perspective()

    def test_resolve(self):
        pass
        #print self.report.resolve(self.request, 'html', 1, 10)
