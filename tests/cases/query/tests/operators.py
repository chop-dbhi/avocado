from django.test import TestCase
from avocado.query.operators import registry as operators

__all__ = ('OperatorTestCase',)


class OperatorTestCase(TestCase):
    def test_null(self):
        op = operators.get('isnull')
        self.assertTrue(op.is_valid(True))
        self.assertTrue(op.is_valid(False))
        self.assertTrue(not op.is_valid(3))
        self.assertTrue(not op.is_valid([]))
        self.assertEqual(op.text(False), 'is not null')
        self.assertEqual(op.text(True), 'is null')

    def test_notnull(self):
        op = operators.get('-isnull')
        self.assertEqual(op.text(False), 'is null')
        self.assertEqual(op.text(True), 'is not null')

    def test_exact(self):
        op = operators.get('exact')
        self.assertTrue(op.is_valid('foo'))
        self.assertTrue(op.is_valid(3))
        self.assertTrue(op.is_valid(True))
        self.assertTrue(not op.is_valid([]))
        self.assertEqual(op.text('foo'), 'is foo')
        self.assertEqual(op.text(3), 'is 3')
        self.assertEqual(op.text(True), 'is True')
        self.assertEqual(op.text(False), 'is False')

    def test_notexact(self):
        # Validity tests same as exact..
        op = operators.get('-exact')
        self.assertEqual(op.text(True), 'is False')
        self.assertEqual(op.text(False), 'is True')
        self.assertEqual(op.text('foo'), 'is not foo')

    def test_iexact(self):
        # String operator..
        op = operators.get('iexact')
        self.assertTrue(op.is_valid('foo'))
        self.assertTrue(not op.is_valid(3))
        self.assertTrue(not op.is_valid(True))
        self.assertTrue(not op.is_valid([]))

    def test_contains(self):
        # Validity tests same as iexact (sting operator)..
        op = operators.get('contains')

    def test_icontains(self):
        # Validity tests same as iexact (sting operator)..
        op = operators.get('icontains')

    def test_lessthan(self):
        op = operators.get('lt')
        self.assertTrue(op.is_valid('foo'))
        self.assertTrue(op.is_valid(3))
        self.assertTrue(op.is_valid(True))
        self.assertTrue(not op.is_valid([]))
        self.assertEqual(op.text('foo'), 'is less than foo')
        self.assertEqual(op.text(3), 'is less than 3')
        self.assertEqual(op.text(True), 'is less than True')

    def test_inlist(self):
        op = operators.get('in')
        self.assertTrue(op.is_valid([]))
        self.assertTrue(op.is_valid([1, 2, 3]))
        self.assertTrue(not op.is_valid('foo'))
        self.assertTrue(not op.is_valid(3))
        self.assertTrue(not op.is_valid(True))
        self.assertEqual(op.text([1]), 'includes 1')
        self.assertEqual(op.text([1, 2]), 'includes 1 and 2')
        self.assertEqual(op.text([1, 2, 3]), 'includes 1, 2 and 3')
        self.assertEqual(op.text([1, 2, 3, 4, 5]), 'includes 1, 2, 3 ... (1 more) and 5')

    def test_notinlist(self):
        op = operators.get('-in')
        self.assertEqual(op.text([1]), 'excludes 1')
        self.assertEqual(op.text([1, 2]), 'excludes 1 and 2')
        self.assertEqual(op.text([1, 2, 3]), 'excludes 1, 2 and 3')

    def test_range(self):
        op = operators.get('range')
        self.assertTrue(op.is_valid([1, 2]))
        self.assertTrue(not op.is_valid([1]))
        self.assertTrue(not op.is_valid([1, 2, 3]))
        self.assertEqual(op.text([1, 2]), 'is between 1 and 2')

    def test_notrange(self):
        op = operators.get('-range')
        self.assertEqual(op.text([1, 2]), 'is not between 1 and 2')

