from django.test import TestCase
from django.core.exceptions import ValidationError

from avocado.fields.operators import *

__all__ = ('OperatorTestCase',)

class OperatorTestCase(TestCase):
    def test_display(self):
        self.assertEqual(str(exact), '= (exact)')
        self.assertEqual(str(iexact), '= (iexact)')
        self.assertEqual(str(contains), 'contains (icontains)')
        self.assertEqual(str(inlist), 'in list (in)')
        self.assertEqual(str(lt), '< (lt)')
        self.assertEqual(str(gt), '> (gt)')
        self.assertEqual(str(lte), '<= (lte)')
        self.assertEqual(str(gte), '>= (gte)')
        self.assertEqual(str(between), 'between (range)')
        self.assertEqual(str(null), 'is null (isnull)')
        self.assertEqual(str(notbetween), 'not between (~range)')
        self.assertEqual(str(notexact), '!= (~exact)')
        self.assertEqual(str(notiexact), '!= (~iexact)')
        self.assertEqual(str(doesnotcontain), 'does not contain (~icontains)')
        self.assertEqual(str(notinlist), 'not in list (~in)')
        self.assertEqual(str(notnull), 'not null (~isnull)')    

    def test_exact(self):
        self.assertTrue(exact.is_valid('foo'))
        self.assertTrue(exact.is_valid(10))
        self.assertFalse(exact.is_valid([1, 2]))

    def test_iexact(self):
        self.assertTrue(iexact.is_valid('foo'))
        self.assertTrue(iexact.is_valid(10))
        self.assertFalse(iexact.is_valid([1, 2]))

    def test_contains(self):
        self.assertTrue(contains.is_valid('foo'))
        self.assertTrue(contains.is_valid(10))
        self.assertFalse(contains.is_valid([1, 2]))

    def test_inlist(self):
        self.assertTrue(inlist.is_valid([1, 2]))
        self.assertFalse(inlist.is_valid('foo'))

    def test_lt(self):
        self.assertTrue(lt.is_valid('foo'))
        self.assertTrue(lt.is_valid(10))
        self.assertFalse(lt.is_valid([1, 2]))

    def test_lte(self):
        self.assertTrue(lte.is_valid('foo'))
        self.assertTrue(lte.is_valid(10))
        self.assertFalse(lte.is_valid([1, 2]))

    def test_gt(self):
        self.assertTrue(gt.is_valid('foo'))
        self.assertTrue(gt.is_valid(10))
        self.assertFalse(gt.is_valid([1, 2]))

    def test_gte(self):
        self.assertTrue(gte.is_valid('foo'))
        self.assertTrue(gte.is_valid(10))
        self.assertFalse(gte.is_valid([1, 2]))

    def test_between(self):
        self.assertTrue(between.is_valid([1, 2]))
        self.assertFalse(between.is_valid('foo'))
        self.assertFalse(between.is_valid([1]))
        self.assertFalse(between.is_valid([1, 2, 3]))

    def test_null(self):
        self.assertTrue(null.is_valid('foo'))
        self.assertTrue(null.is_valid(10))
        self.assertFalse(null.is_valid([1, 2]))

    def test_notbetween(self):
        self.assertTrue(notbetween.is_valid([1, 2]))
        self.assertFalse(notbetween.is_valid('foo'))
        self.assertFalse(notbetween.is_valid([1]))
        self.assertFalse(notbetween.is_valid([1, 2, 3]))

    def test_notexact(self):
        self.assertTrue(notexact.is_valid('foo'))
        self.assertTrue(notexact.is_valid(10))
        self.assertFalse(notexact.is_valid([1, 2]))

    def test_notiexact(self):
        self.assertTrue(notiexact.is_valid('foo'))
        self.assertTrue(notiexact.is_valid(10))
        self.assertFalse(notiexact.is_valid([1, 2]))

    def test_doesnotcontain(self):
        self.assertTrue(doesnotcontain.is_valid('foo'))
        self.assertTrue(doesnotcontain.is_valid(10))
        self.assertFalse(doesnotcontain.is_valid([1, 2]))

    def test_notinlist(self):
        self.assertTrue(notinlist.is_valid([1, 2]))
        self.assertFalse(notinlist.is_valid('foo'))

    def test_notnull(self):
        self.assertTrue(notnull.is_valid('foo'))
        self.assertTrue(notnull.is_valid(10))
        self.assertFalse(notnull.is_valid([1, 2]))