from django.test import TestCase

from avocado.columns.formatters import (AbstractFormatter, FormatterLibrary,
    RegisterError, AlreadyRegisteredError)

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
        
        @library.register
        class AppendItemsFormatter(AbstractFormatter):
            def csv(self, arg):
                arg.append(1)
                return arg
        
        rows = [
            (4, None, 'foo', set([3,4,5]), 10.5, 11.0, 2.0, {}),
            (10, 29, 'foo', [3,4,5], False, 372.19, None, []),
            (None, 'bar', 'foo', None, True, 199.0, 1.0, 192),
        ]

        rows1 = list(library.format(rows, [
            ('Concat Str', 2),
            ('Concat Str', 2),
            ('Add Floats', 3),
            ('Append Items', 1),
        ], 'csv', idx=(0, 8)))
        
        self.assertEqual(rows1, [
            ('4 None', 'foo set([3, 4, 5])', 23.5, 'error'),
            ('10 29', 'foo [3, 4, 5]', None, [1]),
            ('None bar', 'foo None', None, 'error'),
        ])

    # def test_no_formatters(self):
    #     rows = [
    #         (4, None, 'foo', set([3,4,5]), 129),
    #         (10, 29, 'foo', [3,4,5], False),
    #         (None, 'bar', 'foo', None, True),
    #     ]
    #     
    #     rows1 = list(self.library.format(rows, [(None, 2), ('', 2)],
    #         idx=(None, 4)))
    #     
    #     self.assertEqual(rows1, [
    #         ('4 None', 'foo set([3, 4, 5])', 129),
    #         ('10 29', 'foo [3, 4, 5]', False),
    #         ('None bar', 'foo None', True),
    #     ])
    #     
    #     rows2 = list(self.library.format(rows, [(0, 1), ('afunc', 3)],
    #         idx=(1, None)))
    #     
    #     self.assertEqual(rows2, [
    #         (4, 'None', 'foo set([3, 4, 5]) 129'),
    #         (10, '29', 'foo [3, 4, 5] False'),
    #         (None,  'bar', 'foo None True'),
    #     ])
    # 
    #     # if an 'empty' rule is provided, it is skipped
    #     rows3 = list(self.library.format(rows, [(None, 0), ('afunc', 2)],
    #         idx=(1, None)))
    #     
    #     self.assertEqual(rows3, [
    #         (4, 'None foo'),
    #         (10, '29 foo'),
    #         (None, 'bar foo'),
    #     ])
    # 
    # def test_register(self):
    #     @self.library.register
    #     def func1(arg1, arg2):
    #         return arg1 + arg2
    #     
    #     self.assertEqual(func1(5, 5), self.library.get('func1')(5, 5))
    #     
    #     @self.library.register('foo bar')
    #     def func2(arg1):
    #         return '%s is a cool arg' % arg1
    #     
    #     self.assertEqual(func2(5), self.library.get('func2')(5))
    # 
    #     @self.library.register('boolean')
    #     def func3(arg1):
    #         return arg1 and 'Yes' or 'No'
    # 
    #     self.assertEqual(func3(None), self.library.get('func3')(None))
    #     
    #     def func3(arg1):
    #         return
    #     
    #     self.assertRaises(RegisterError, self.library.register('another'), func3)
    # 
    # def test_formatters(self):
    #     self.test_register()
    #     
    #     rows = [
    #         (4, None, 'foo', set([3,4,5]), 129),
    #         (10, 29, 'foo', [3,4,5], False),
    #         (None, 'bar', 'foo', None, True),
    #     ]
    #     
    #     rows1 = list(self.library.format(rows, [('func1', 2), ('', 2)],
    #         idx=(None, 4)))
    #     
    #     self.assertEqual(rows1, [
    #         ('(data format error)', 'foo set([3, 4, 5])', 129),
    #         (39, 'foo [3, 4, 5]', False),
    #         ('(data format error)', 'foo None', True),
    #     ])
    #     
    #     rows2 = list(self.library.format(rows, [('func2', 1), ('', 2), ('func3', 1)],
    #         idx=(1, None)))
    #     
    #     self.assertEqual(rows2, [
    #         (4, 'None is a cool arg', 'foo set([3, 4, 5])', 'Yes'),
    #         (10, '29 is a cool arg', 'foo [3, 4, 5]',  'No'),
    #         (None,  'bar is a cool arg', 'foo None', 'Yes'),
    #     ])
    # 
    # def test_choices(self):
    #     self.test_register()
    #     
    #     self.assertEqual(self.library.choices, [('func3', 'boolean'),
    #         ('func2', 'foo bar'), ('func1', 'func1')])
    # 