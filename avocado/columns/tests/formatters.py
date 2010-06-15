from django.test import TestCase

from avocado.columns.formatters import (AbstractFormatter, FormatterLibrary,
    RegisterError, AlreadyRegisteredError, RemoveFormatter, IgnoreFormatter)

__all__ = ('FormatterLibraryTestCase',)

class FormatterLibraryTestCase(TestCase):
    def test_no_formatters(self):
        library = FormatterLibrary()
        self.assertEqual(library._cache, {})

    def test_bad_register(self):
        library = FormatterLibrary({
            'csv': {
                'error': 'error'
            }
        })

        class DumbFormatter(object):
            def csv(self, arg1, arg2):
                return ' '.join([str(arg1), str(arg2)])

        self.assertRaises(RegisterError, library.register, DumbFormatter)

    def test_single_format(self):
        library = FormatterLibrary({
            'csv': {
                'error': 'error'
            }
        })

        self.assertEqual(library._cache, {
            'csv': {
                'error': 'error',
                'formatters': {}
            }
        })

        @library.register
        class ConcatStrFormatter(AbstractFormatter):
            def csv(self, *args):
                return ' '.join(map(lambda x: str(x), args))


        @library.register
        class AddFloats(AbstractFormatter):
            name = 'Add Floats'
            def csv(self, *args):
                if not all(map(lambda x: type(x) is float, args)):
                    return None
                return sum(args)


        self.assertRaises(AlreadyRegisteredError, library.register, AddFloats)
        self.assertEqual(library.choices('csv'), [('Add Floats', 'Add Floats'),
            ('Concat Str', 'Concat Str')])

        library.register(RemoveFormatter)
        library.register(IgnoreFormatter)

        @library.register
        class AddOneFormatter(AbstractFormatter):
            def csv(self, arg):
                return arg + 1

        rows = [
            (4, None, 'remove me', 'foo', set([3,4,5]), 'ignore me', 10.5, 11.0, 2.0, {}),
            (10, 29, 292, 'foo', [3,4,5], 9999, False, 372.19, None, []),
            (None, 'bar', 'rem', 'foo', None, 'moo', True, 199.0, 1.0, 192),
        ]

        rows1 = list(library.format(rows, [
            ('Concat Str', 2),
            ('Remove', 1),
            ('Concat Str', 2),
            ('Ignore', 1),
            ('Add Floats', 3),
            ('Add One', 1),
        ], 'csv'))

        self.assertEqual(rows1, [
            ('4 None', 'foo set([3, 4, 5])', 'ignore me', 23.5, 'error'),
            ('10 29', 'foo [3, 4, 5]', 9999, None, 'error'),
            ('None bar', 'foo None', 'moo', None, 193),
        ])
