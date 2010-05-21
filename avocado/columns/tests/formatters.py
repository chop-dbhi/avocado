from copy import deepcopy

from django.test import TestCase

from avocado.columns.formatters import (JSONFormatterLibrary, FormatterLibrary,
    RegisterError)
    
__all__ = ('FormatterLibraryTestCase', 'JSONFormatterLibraryTestCase')

class FormatterLibraryTestCase(TestCase):
    def setUp(self):
        super(FormatterLibraryTestCase, self).setUp()
        self.library = FormatterLibrary()

    def test_no_formatters(self):
        rows = [
            (4, None, 'foo', set([3,4,5]), 129),
            (10, 29, 'foo', [3,4,5], False),
            (None, 'bar', 'foo', None, True),
        ]
        
        rows1 = list(self.library.format(rows, [(None, 2), ('', 2)],
            idx=(None, 4)))
        
        self.assertEqual(rows1, [
            ('4 None', 'foo set([3, 4, 5])', 129),
            ('10 29', 'foo [3, 4, 5]', False),
            ('None bar', 'foo None', True),
        ])
        
        rows2 = list(self.library.format(rows, [(0, 1), ('afunc', 3)],
            idx=(1, None)))
        
        self.assertEqual(rows2, [
            (4, 'None', 'foo set([3, 4, 5]) 129'),
            (10, '29', 'foo [3, 4, 5] False'),
            (None,  'bar', 'foo None True'),
        ])

        # if an 'empty' rule is provided, it is skipped
        rows3 = list(self.library.format(rows, [(None, 0), ('afunc', 2)],
            idx=(1, None)))
        
        self.assertEqual(rows3, [
            (4, 'None foo'),
            (10, '29 foo'),
            (None, 'bar foo'),
        ])

    def test_register(self):
        @self.library.register
        def func1(arg1, arg2):
            return arg1 + arg2
        
        self.assertEqual(func1(5, 5), self.library.get('func1')(5, 5))
        
        @self.library.register('foo bar')
        def func2(arg1):
            return '%s is a cool arg' % arg1
        
        self.assertEqual(func2(5), self.library.get('func2')(5))

        @self.library.register('boolean')
        def func3(arg1):
            return arg1 and 'Yes' or 'No'

        self.assertEqual(func3(None), self.library.get('func3')(None))
        
        def func3(arg1):
            return
        
        self.assertRaises(RegisterError, self.library.register('another'), func3)

    def test_formatters(self):
        self.test_register()
        
        rows = [
            (4, None, 'foo', set([3,4,5]), 129),
            (10, 29, 'foo', [3,4,5], False),
            (None, 'bar', 'foo', None, True),
        ]
        
        rows1 = list(self.library.format(rows, [('func1', 2), ('', 2)],
            idx=(None, 4)))
        
        self.assertEqual(rows1, [
            ('(data format error)', 'foo set([3, 4, 5])', 129),
            (39, 'foo [3, 4, 5]', False),
            ('(data format error)', 'foo None', True),
        ])
        
        rows2 = list(self.library.format(rows, [('func2', 1), ('', 2), ('func3', 1)],
            idx=(1, None)))
        
        self.assertEqual(rows2, [
            (4, 'None is a cool arg', 'foo set([3, 4, 5])', 'Yes'),
            (10, '29 is a cool arg', 'foo [3, 4, 5]',  'No'),
            (None,  'bar is a cool arg', 'foo None', 'Yes'),
        ])

    def test_choices(self):
        self.test_register()
        
        self.assertEqual(self.library.choices, [('func3', 'boolean'),
            ('func2', 'foo bar'), ('func1', 'func1')])


class JSONFormatterLibraryTestCase(TestCase):
    def setUp(self):
        super(JSONFormatterLibraryTestCase, self).setUp()
        self.library = JSONFormatterLibrary()

    def test_no_formatters(self):
        data = [
            {'id': 1, 'data': (4, None, 'foo', set([3,4,5]), 129)},
            {'id': 2, 'data': (10, 29, 'foo', [3,4,5], False)},
            {'id': 3, 'data': (None, 'bar', 'foo', None, True)},
        ]
        
        data1 = list(self.library.format(deepcopy(data), [(None, 2), ('', 2)],
            idx=(None, 4)))
        
        self.assertEqual(data1, [
            {'id': 1, 'data': ('4 None', 'foo set([3, 4, 5])', 129)},
            {'id': 2, 'data': ('10 29', 'foo [3, 4, 5]', False)},
            {'id': 3, 'data': ('None bar', 'foo None', True)},
        ])
        
        data2 = list(self.library.format(deepcopy(data), [(0, 1), ('afunc', 3)],
            idx=(1, None)))
        
        self.assertEqual(data2, [
            {'id': 1, 'data': (4, 'None', 'foo set([3, 4, 5]) 129')},
            {'id': 2, 'data': (10, '29', 'foo [3, 4, 5] False')},
            {'id': 3, 'data': (None,  'bar', 'foo None True')},
        ])

        # if an 'empty' rule is provided, it is skipped
        data3 = list(self.library.format(deepcopy(data), [(None, 0), ('afunc', 2)],
            idx=(1, None)))
        
        self.assertEqual(data3, [
            {'id': 1, 'data': (4, 'None foo')},
            {'id': 2, 'data': (10, '29 foo')},
            {'id': 3, 'data': (None, 'bar foo')},
        ])

    def test_register(self):
        @self.library.register
        def func1(arg1, arg2):
            return arg1 + arg2
        
        self.assertEqual(func1(5, 5), self.library.get('func1')(5, 5))
        
        @self.library.register('foo bar')
        def func2(arg1):
            return '%s is a cool arg' % arg1
        
        self.assertEqual(func2(5), self.library.get('func2')(5))

        @self.library.register('boolean')
        def func3(arg1):
            return arg1 and 'Yes' or 'No'

        self.assertEqual(func3(None), self.library.get('func3')(None))
        
        def func3(arg1):
            return
        
        self.assertRaises(RegisterError, self.library.register('another'), func3)

    def test_formatters(self):
        self.test_register()
        
        data = [
            {'id': 1, 'data': (4, None, 'foo', set([3,4,5]), 129)},
            {'id': 2, 'data': (10, 29, 'foo', [3,4,5], False)},
            {'id': 3, 'data': (None, 'bar', 'foo', None, True)},
        ]
        
        data1 = list(self.library.format(deepcopy(data), [('func1', 2), ('', 2)],
            idx=(None, 4)))
        
        self.assertEqual(data1, [
            {'id': 1, 'data': ('<span class="data-format-error">(data format error)</span>', 'foo set([3, 4, 5])', 129)},
            {'id': 2, 'data': (39, 'foo [3, 4, 5]', False)},
            {'id': 3, 'data': ('<span class="data-format-error">(data format error)</span>', 'foo None', True)},
        ])
        
        data2 = list(self.library.format(deepcopy(data), [('func2', 1), ('', 2), ('func3', 1)],
            idx=(1, None), key='data'))
        
        self.assertEqual(data2, [
            {'id': 1, 'data': (4, 'None is a cool arg', 'foo set([3, 4, 5])', 'Yes')},
            {'id': 2, 'data': (10, '29 is a cool arg', 'foo [3, 4, 5]',  'No')},
            {'id': 3, 'data': (None,  'bar is a cool arg', 'foo None', 'Yes')},
        ])
    
    def test_choices(self):
        self.test_register()
        
        self.assertEqual(self.library.choices, [('func3', 'boolean'),
            ('func2', 'foo bar'), ('func1', 'func1')])