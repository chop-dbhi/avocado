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

        self.assertEqual(unicode(exact), u'= (exact)')
        self.assertEqual(unicode(iexact), u'= (iexact)')
        self.assertEqual(unicode(contains), u'contains (icontains)')
        self.assertEqual(unicode(inlist), u'in list (in)')
        self.assertEqual(unicode(lt), u'< (lt)')
        self.assertEqual(unicode(gt), u'> (gt)')
        self.assertEqual(unicode(lte), u'<= (lte)')
        self.assertEqual(unicode(gte), u'>= (gte)')
        self.assertEqual(unicode(between), u'between (range)')
        self.assertEqual(unicode(null), u'is null (isnull)')
        self.assertEqual(unicode(notbetween), u'not between (~range)')
        self.assertEqual(unicode(notexact), u'!= (~exact)')
        self.assertEqual(unicode(notiexact), u'!= (~iexact)')
        self.assertEqual(unicode(doesnotcontain), u'does not contain (~icontains)')
        self.assertEqual(unicode(notinlist), u'not in list (~in)')
        self.assertEqual(unicode(notnull), u'not null (~isnull)')

    def test_exact(self):
        self.assertTrue(exact.check('foo'))
        self.assertTrue(exact.check(10))
        self.assertFalse(exact.check([1, 2]))

    def test_iexact(self):
        self.assertTrue(iexact.check('foo'))
        self.assertTrue(iexact.check(10))
        self.assertFalse(iexact.check([1, 2]))

    def test_contains(self):
        self.assertTrue(contains.check('foo'))
        self.assertTrue(contains.check(10))
        self.assertFalse(contains.check([1, 2]))

    def test_inlist(self):
        self.assertTrue(inlist.check([1, 2]))
        self.assertFalse(inlist.check('foo'))

    def test_lt(self):
        self.assertTrue(lt.check('foo'))
        self.assertTrue(lt.check(10))
        self.assertFalse(lt.check([1, 2]))

    def test_lte(self):
        self.assertTrue(lte.check('foo'))
        self.assertTrue(lte.check(10))
        self.assertFalse(lte.check([1, 2]))

    def test_gt(self):
        self.assertTrue(gt.check('foo'))
        self.assertTrue(gt.check(10))
        self.assertFalse(gt.check([1, 2]))

    def test_gte(self):
        self.assertTrue(gte.check('foo'))
        self.assertTrue(gte.check(10))
        self.assertFalse(gte.check([1, 2]))

    def test_between(self):
        self.assertTrue(between.check([1, 2]))
        self.assertFalse(between.check('foo'))
        self.assertFalse(between.check([1]))
        self.assertFalse(between.check([1, 2, 3]))

    def test_null(self):
        self.assertTrue(null.check('foo'))
        self.assertTrue(null.check(10))
        self.assertFalse(null.check([1, 2]))

    def test_notbetween(self):
        self.assertTrue(notbetween.check([1, 2]))
        self.assertFalse(notbetween.check('foo'))
        self.assertFalse(notbetween.check([1]))
        self.assertFalse(notbetween.check([1, 2, 3]))

    def test_notexact(self):
        self.assertTrue(notexact.check('foo'))
        self.assertTrue(notexact.check(10))
        self.assertFalse(notexact.check([1, 2]))

    def test_notiexact(self):
        self.assertTrue(notiexact.check('foo'))
        self.assertTrue(notiexact.check(10))
        self.assertFalse(notiexact.check([1, 2]))

    def test_doesnotcontain(self):
        self.assertTrue(doesnotcontain.check('foo'))
        self.assertTrue(doesnotcontain.check(10))
        self.assertFalse(doesnotcontain.check([1, 2]))

    def test_notinlist(self):
        self.assertTrue(notinlist.check([1, 2]))
        self.assertFalse(notinlist.check('foo'))

    def test_notnull(self):
        self.assertTrue(notnull.check('foo'))
        self.assertTrue(notnull.check(10))
        self.assertFalse(notnull.check([1, 2]))
