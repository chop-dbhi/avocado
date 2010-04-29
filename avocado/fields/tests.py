from django.test import TestCase

from avocado.fields import operators as ops

__all__ = ('OperatorTestCase',)

class OperatorTestCase(TestCase):
    def test_display(self):
        self.assertEqual(str(ops.exact), '= (exact)')
        self.assertEqual(str(ops.iexact), '= (iexact)')
        self.assertEqual(str(ops.contains), 'contains (icontains)')
        self.assertEqual(str(ops.inlist), 'in list (in)')
        self.assertEqual(str(ops.lt), '< (lt)')
        self.assertEqual(str(ops.gt), '> (gt)')
        self.assertEqual(str(ops.lte), '<= (lte)')
        self.assertEqual(str(ops.gte), '>= (gte)')
        self.assertEqual(str(ops.between), 'between (range)')
        self.assertEqual(str(ops.null), 'is null (isnull)')
        self.assertEqual(str(ops.notbetween), 'not between (~range)')
        self.assertEqual(str(ops.notexact), 'not = (~exact)')
        self.assertEqual(str(ops.notiexact), 'not = (~iexact)')
        self.assertEqual(str(ops.doesnotcontain), 'does not contain (~icontains)')
        self.assertEqual(str(ops.notinlist), 'not in list (~in)')
        self.assertEqual(str(ops.notnull), 'not null (~isnull)')
    
    def test_exact(self):
        self.assertEqual(ops.exact.clean('foo'), 'foo')
        self.assertEqual(ops.exact.clean(True), True)
        self.assertEqual(ops.exact.clean([2, 4]), 2)
        self.assertEqual(ops.exact.clean([4]), 4)

    def test_iexact(self):
        self.assertEqual(ops.iexact.clean('foo'), 'foo')
        self.assertEqual(ops.iexact.clean(True), True)
        self.assertEqual(ops.iexact.clean([2, 4]), 2)
        self.assertEqual(ops.iexact.clean([4]), 4)

    def test_contains(self):
        self.assertEqual(ops.contains.clean('foo'), 'foo')
        self.assertEqual(ops.contains.clean(True), True)
        self.assertEqual(ops.contains.clean([2, 4]), 2)
        self.assertEqual(ops.contains.clean([4]), 4)

    def test_inlist(self):
        self.assertEqual(ops.inlist.clean('foo'), ['foo'])
        self.assertEqual(ops.inlist.clean('hello\nworld'), ['hello', 'world'])
        self.assertEqual(ops.inlist.clean([2, 4]), [2, 4])
        self.assertEqual(ops.inlist.clean([4]), [4])

    def test_lt(self):
        self.assertEqual(ops.lt.clean('foo'), 'foo')
        self.assertEqual(ops.lt.clean(True), True)
        self.assertEqual(ops.lt.clean([2, 4]), 2)
        self.assertEqual(ops.lt.clean([4]), 4)

    def test_gt(self):
        self.assertEqual(ops.gt.clean('foo'), 'foo')
        self.assertEqual(ops.gt.clean(True), True)
        self.assertEqual(ops.gt.clean([2, 4]), 2)
        self.assertEqual(ops.gt.clean([4]), 4)

    def test_lte(self):
        self.assertEqual(ops.lte.clean('foo'), 'foo')
        self.assertEqual(ops.lte.clean(True), True)
        self.assertEqual(ops.lte.clean([2, 4]), 2)
        self.assertEqual(ops.lte.clean([4]), 4)

    def test_gte(self):
        self.assertEqual(ops.gte.clean('foo'), 'foo')
        self.assertEqual(ops.gte.clean(True), True)
        self.assertEqual(ops.gte.clean([2, 4]), 2)
        self.assertEqual(ops.gte.clean([4]), 4)

    def test_between(self):
        self.assertRaises(ops.ValidationError, ops.notbetween.clean, 'foo')
        self.assertRaises(ops.ValidationError, ops.notbetween.clean, [4])
        self.assertEqual(ops.between.clean([2, 4]), [2, 4])
        self.assertEqual(ops.between.clean(['foo', False]), ['foo', False])

    def test_null(self):
        self.assertEqual(ops.null.clean('foo'), 'foo')
        self.assertEqual(ops.null.clean(True), True)
        self.assertEqual(ops.null.clean([2, 4]), 2)
        self.assertEqual(ops.null.clean([4]), 4)

    def test_notbetween(self):
        self.assertRaises(ops.ValidationError, ops.notbetween.clean, 'foo')
        self.assertRaises(ops.ValidationError, ops.notbetween.clean, [4])
        self.assertEqual(ops.notbetween.clean([2, 4]), [2, 4])
        self.assertEqual(ops.notbetween.clean(['foo', False]), ['foo', False])

    def test_notexact(self):
        self.assertEqual(ops.notexact.clean('foo'), 'foo')
        self.assertEqual(ops.notexact.clean(True), True)
        self.assertEqual(ops.notexact.clean([2, 4]), 2)
        self.assertEqual(ops.notexact.clean([4]), 4)

    def test_notiexact(self):
        self.assertEqual(ops.notiexact.clean('foo'), 'foo')
        self.assertEqual(ops.notiexact.clean(True), True)
        self.assertEqual(ops.notiexact.clean([2, 4]), 2)
        self.assertEqual(ops.notiexact.clean([4]), 4)

    def test_doesnotcontain(self):
        self.assertEqual(ops.doesnotcontain.clean('foo'), 'foo')
        self.assertEqual(ops.doesnotcontain.clean(True), True)
        self.assertEqual(ops.doesnotcontain.clean([2, 4]), 2)
        self.assertEqual(ops.doesnotcontain.clean([4]), 4)

    def test_notinlist(self):
        self.assertEqual(ops.notinlist.clean('foo'), ['foo'])
        self.assertEqual(ops.notinlist.clean('hello\nworld'), ['hello', 'world'])
        self.assertEqual(ops.notinlist.clean([2, 4]), [2, 4])
        self.assertEqual(ops.notinlist.clean([4]), [4])

    def test_notnull(self):
        self.assertEqual(ops.notnull.clean('foo'), 'foo')
        self.assertEqual(ops.notnull.clean(True), True)
        self.assertEqual(ops.notnull.clean([2, 4]), 2)
        self.assertEqual(ops.notnull.clean([4]), 4)