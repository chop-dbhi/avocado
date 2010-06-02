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
        self.assertEqual(exact.validate('foo'), None)
        self.assertEqual(exact.validate(10), None)
        self.assertRaises(ValidationError, exact.validate, [1, 2])

    def test_iexact(self):
        self.assertEqual(iexact.validate('foo'), None)
        self.assertEqual(iexact.validate(10), None)
        self.assertRaises(ValidationError, iexact.validate, [1, 2])

    def test_contains(self):
        self.assertEqual(contains.validate('foo'), None)
        self.assertEqual(contains.validate(10), None)
        self.assertRaises(ValidationError, contains.validate, [1, 2])

    def test_inlist(self):
        self.assertEqual(inlist.validate([1, 2]), None)
        self.assertRaises(ValidationError, inlist.validate, 'foo')

    def test_lt(self):
        self.assertEqual(lt.validate('foo'), None)
        self.assertEqual(lt.validate(10), None)
        self.assertRaises(ValidationError, lt.validate, [1, 2])

    def test_lte(self):
        self.assertEqual(lte.validate('foo'), None)
        self.assertEqual(lte.validate(10), None)
        self.assertRaises(ValidationError, lte.validate, [1, 2])

    def test_gt(self):
        self.assertEqual(gt.validate('foo'), None)
        self.assertEqual(gt.validate(10), None)
        self.assertRaises(ValidationError, gt.validate, [1, 2])

    def test_gte(self):
        self.assertEqual(gte.validate('foo'), None)
        self.assertEqual(gte.validate(10), None)
        self.assertRaises(ValidationError, gte.validate, [1, 2])

    def test_between(self):
        self.assertEqual(between.validate([1, 2]), None)
        self.assertRaises(ValidationError, between.validate, 'foo')
        self.assertRaises(ValidationError, between.validate, [1])
        self.assertRaises(ValidationError, between.validate, [1, 2, 3])

    def test_null(self):
        self.assertEqual(null.validate('foo'), None)
        self.assertEqual(null.validate(10), None)
        self.assertRaises(ValidationError, null.validate, [1, 2])

    def test_notbetween(self):
        self.assertEqual(notbetween.validate([1, 2]), None)
        self.assertRaises(ValidationError, notbetween.validate, 'foo')
        self.assertRaises(ValidationError, notbetween.validate, [1])
        self.assertRaises(ValidationError, notbetween.validate, [1, 2, 3])

    def test_notexact(self):
        self.assertEqual(notexact.validate('foo'), None)
        self.assertEqual(notexact.validate(10), None)
        self.assertRaises(ValidationError, notexact.validate, [1, 2])

    def test_notiexact(self):
        self.assertEqual(notiexact.validate('foo'), None)
        self.assertEqual(notiexact.validate(10), None)
        self.assertRaises(ValidationError, notiexact.validate, [1, 2])

    def test_doesnotcontain(self):
        self.assertEqual(doesnotcontain.validate('foo'), None)
        self.assertEqual(doesnotcontain.validate(10), None)
        self.assertRaises(ValidationError, doesnotcontain.validate, [1, 2])

    def test_notinlist(self):
        self.assertEqual(notinlist.validate([1, 2]), None)
        self.assertRaises(ValidationError, notinlist.validate, 'foo')

    def test_notnull(self):
        self.assertEqual(notnull.validate('foo'), None)
        self.assertEqual(notnull.validate(10), None)
        self.assertRaises(ValidationError, notnull.validate, [1, 2])