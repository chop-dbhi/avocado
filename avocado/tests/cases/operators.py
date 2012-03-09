from avocado.tests.base import BaseTestCase
from avocado.query.operators import registry

__all__ = ('OperatorTestCase',)

class OperatorTestCase(BaseTestCase):
    def test_null(self):
        op = registry.get('isnull')
        self.assertTrue(op.is_valid(True))
        self.assertTrue(op.is_valid(False))
        self.assertTrue(not op.is_valid(3))
        self.assertTrue(not op.is_valid([]))
        self.assertEqual(op.text(False), 'is not null')
        self.assertEqual(op.text(True), 'is null')

    def test_notnull(self):
        op = registry.get('-isnull')
        self.assertEqual(op.text(False), 'is null')
        self.assertEqual(op.text(True), 'is not null')

    def test_exact(self):
        op = registry.get('exact')
        self.assertTrue(op.is_valid('foo'))
        self.assertTrue(op.is_valid(3))
        self.assertTrue(op.is_valid(True))
        self.assertTrue(not op.is_valid([]))
        self.assertEqual(op.text('foo'), 'is equal to foo')
        self.assertEqual(op.text(3), 'is equal to 3')
        self.assertEqual(op.text(True), 'is True')
        self.assertEqual(op.text(False), 'is False')

    def test_notexact(self):
        # Validity tests same as exact..
        op = registry.get('-exact')
        self.assertEqual(op.text(True), 'is False')
        self.assertEqual(op.text(False), 'is True')

    def test_iexact(self):
        # String operator..
        op = registry.get('iexact')
        self.assertTrue(op.is_valid('foo'))
        self.assertTrue(not op.is_valid(3))
        self.assertTrue(not op.is_valid(True))
        self.assertTrue(not op.is_valid([]))

    def test_contains(self):
        # Validity tests same as iexact (sting operator)..
        op = registry.get('contains')

    def test_icontains(self):
        # Validity tests same as iexact (sting operator)..
        op = registry.get('icontains')

    def test_lessthan(self):
        op = registry.get('lt')
        self.assertTrue(op.is_valid('foo'))
        self.assertTrue(op.is_valid(3))
        self.assertTrue(op.is_valid(True))
        self.assertTrue(not op.is_valid([]))
        self.assertEqual(op.text('foo'), 'is less than foo')
        self.assertEqual(op.text(3), 'is less than 3')
        self.assertEqual(op.text(True), 'is less than True')

    def test_inlist(self):
        op = registry.get('in')
        self.assertTrue(op.is_valid([]))
        self.assertTrue(op.is_valid([1, 2, 3]))
        self.assertTrue(not op.is_valid('foo'))
        self.assertTrue(not op.is_valid(3))
        self.assertTrue(not op.is_valid(True))
        self.assertEqual(op.text([1]), 'is equal to 1')
        self.assertEqual(op.text([1, 2]), 'is either 1 or 2')
        self.assertEqual(op.text([1, 2, 3]), 'is either 1, 2 or 3')
        self.assertEqual(op.text([1, 2, 3, 4, 5]), 'is either 1, 2, 3 ... (1 more) or 5')

    def test_notinlist(self):
        op = registry.get('-in')
        self.assertEqual(op.text([1]), 'is not equal to 1')
        self.assertEqual(op.text([1, 2]), 'is neither 1 nor 2')
        self.assertEqual(op.text([1, 2, 3]), 'is neither 1, 2 nor 3')

    def test_range(self):
        op = registry.get('range')
        self.assertTrue(op.is_valid([1, 2]))
        self.assertTrue(not op.is_valid([1]))
        self.assertTrue(not op.is_valid([1, 2, 3]))
        self.assertEqual(op.text([1, 2]), 'is between 1 and 2')

    def test_notrange(self):
        op = registry.get('-range')
        self.assertEqual(op.text([1, 2]), 'is not between 1 and 2')

