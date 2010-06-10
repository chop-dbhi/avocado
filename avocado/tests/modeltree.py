from django.test import TestCase

from avocado.tests.models import *
from avocado.modeltree import ModelTree

__all__ = ('ModelTreeTestCase',)

class ModelTreeTestCase(TestCase):
    def setUp(self):
        self.root = ModelTree(Root)
        self.parent1 = ModelTree(Parent1)
        self.parent2 = ModelTree(Parent2)
        self.bear = ModelTree(Bear)

        self.root_to_foo = self.root.path_to(Foo)
        self.root_to_baz = self.root.path_to(Baz)
        self.root_to_child2 = self.root.path_to(Child2)

        self.parent1_to_child1 = self.parent1.path_to(Child1)
        self.parent1_to_root = self.parent1.path_to(Root)
        self.parent1_to_bar = self.parent1.path_to(Bar)

        self.parent2_to_child2 = self.parent2.path_to(Child2)
        self.parent2_to_baz = self.parent2.path_to(Baz)
        self.parent2_to_bear = self.parent2.path_to(Bear)
        
        self.bear_to_bar = self.bear.path_to(Bar)
        self.bear_to_parent1 = self.bear.path_to(Parent1)
        self.bear_to_root = self.bear.path_to(Root)

    def test_children_length(self):
        "Test to ensure the children count are correct"
        self.assertEqual(len(self.root.root_node.children), 4)
        self.assertEqual(len(self.parent1.root_node.children), 2)
        self.assertEqual(len(self.parent2.root_node.children), 2)
        self.assertEqual(len(self.bear.root_node.children), 1)

    def test_node_path_size(self):
        "Test to ensure the correct node_path size"
        self.assertEqual(len(self.root_to_foo), 2)
        self.assertEqual(len(self.root_to_baz), 2)        
        self.assertEqual(len(self.root_to_child2), 2)

        self.assertEqual(len(self.parent1_to_child1), 1)
        self.assertEqual(len(self.parent1_to_root), 1)        
        self.assertEqual(len(self.parent1_to_bar), 2)

        self.assertEqual(len(self.parent2_to_child2), 1)
        self.assertEqual(len(self.parent2_to_baz), 3)
        self.assertEqual(len(self.parent2_to_bear), 4)
        
        self.assertEqual(len(self.bear_to_bar), 2)
        self.assertEqual(len(self.bear_to_parent1), 4)
        self.assertEqual(len(self.bear_to_root), 3)

    def test_node_path(self):
        "Test to ensure the correct path is generated"
        self.assertEqual([n.name for n in self.root_to_foo],
            ['Child3', 'Foo'])
        self.assertEqual([n.name for n in self.root_to_baz],
            ['Bar', 'Baz'])
        self.assertEqual([n.name for n in self.root_to_child2],
            ['Parent2', 'Child2'])

        self.assertEqual([n.name for n in self.parent1_to_child1],
            ['Child1'])
        self.assertEqual([n.name for n in self.parent1_to_root],
            ['Root'])
        self.assertEqual([n.name for n in self.parent1_to_bar],
            ['Root', 'Bar'])

        self.assertEqual([n.name for n in self.parent2_to_child2],
            ['Child2'])
        self.assertEqual([n.name for n in self.parent2_to_baz],
            ['Child2', 'Bar', 'Baz'])
        self.assertEqual([n.name for n in self.parent2_to_bear],
            ['Child2', 'Bar', 'Baz', 'Bear'])

        self.assertEqual([n.name for n in self.bear_to_bar],
            ['Baz', 'Bar'])
        self.assertEqual([n.name for n in self.bear_to_parent1],
            ['Baz', 'Bar', 'Root', 'Parent1'])
        self.assertEqual([n.name for n in self.bear_to_root],
            ['Baz', 'Bar', 'Root'])

    def test_related_name_path(self):
        "Test to ensure the correct related names are used."
        self.assertEqual(self.root.related_name_path(self.root_to_foo),
            ['child3', 'fooey'])
        self.assertEqual(self.root.related_name_path(self.root_to_baz),
            ['barman', 'baz'])
        self.assertEqual(self.root.related_name_path(self.root_to_child2),
            ['wacky_parent', 'child2'])
    
        self.assertEqual(self.parent1.related_name_path(self.parent1_to_child1),
            ['child1'])
        self.assertEqual(self.parent1.related_name_path(self.parent1_to_root),
            ['parent'])
        self.assertEqual(self.parent1.related_name_path(self.parent1_to_bar),
            ['parent', 'barman'])
    
        self.assertEqual(self.parent2.related_name_path(self.parent2_to_child2),
            ['child2'])
        self.assertEqual(self.parent2.related_name_path(self.parent2_to_baz),
            ['child2', 'bar', 'baz'])
        self.assertEqual(self.parent2.related_name_path(self.parent2_to_bear),
            ['child2', 'bar', 'baz', 'many_bears'])

        self.assertEqual(self.bear.related_name_path(self.bear_to_bar),
            ['bazes', 'parent'])
        self.assertEqual(self.bear.related_name_path(self.bear_to_parent1),
            ['bazes', 'parent', 'root', 'crazy_parent'])
        self.assertEqual(self.bear.related_name_path(self.bear_to_root),
            ['bazes', 'parent', 'root'])

    def test_accessor_name_path(self):
        "Test to ensure the accessor names are correct."
        pairs = self.root.get_accessor_pairs(self.root_to_foo)
        self.failUnless(all([hasattr(n.model, attr) for n, attr in pairs]))
        pairs = self.root.get_accessor_pairs(self.root_to_baz)
        self.failUnless(all([hasattr(n.model, attr) for n, attr in pairs]))
        pairs = self.root.get_accessor_pairs(self.root_to_child2)
        self.failUnless(all([hasattr(n.model, attr) for n, attr in pairs]))

        pairs = self.parent1.get_accessor_pairs(self.parent1_to_child1)
        self.failUnless(all([hasattr(n.model, attr) for n, attr in pairs]))
        pairs = self.parent1.get_accessor_pairs(self.parent1_to_root)
        self.failUnless(all([hasattr(n.model, attr) for n, attr in pairs]))
        pairs = self.parent1.get_accessor_pairs(self.parent1_to_bar)
        self.failUnless(all([hasattr(n.model, attr) for n, attr in pairs]))

        pairs = self.parent2.get_accessor_pairs(self.parent2_to_child2)
        self.failUnless(all([hasattr(n.model, attr) for n, attr in pairs]))
        pairs = self.parent2.get_accessor_pairs(self.parent2_to_baz)
        self.failUnless(all([hasattr(n.model, attr) for n, attr in pairs]))
        pairs = self.parent2.get_accessor_pairs(self.parent2_to_bear)
        self.failUnless(all([hasattr(n.model, attr) for n, attr in pairs]))
    
        pairs = self.bear.get_accessor_pairs(self.bear_to_bar)
        self.failUnless(all([hasattr(n.model, attr) for n, attr in pairs]))
        pairs = self.bear.get_accessor_pairs(self.bear_to_parent1)
        self.failUnless(all([hasattr(n.model, attr) for n, attr in pairs]))
        pairs = self.bear.get_accessor_pairs(self.bear_to_root)
        self.failUnless(all([hasattr(n.model, attr) for n, attr in pairs]))

    def test_join_connections(self):
        self.assertEqual(self.root.get_all_join_connections(self.root_to_foo),
            [(None, 'tests_root', None, None),('tests_root', 'tests_child3', 'id', 'parent_id'),
            ('tests_child3', 'tests_foo', 'id', 'parent_id')])
        self.assertEqual(self.root.get_all_join_connections(self.root_to_baz),
            [(None, 'tests_root', None, None), ('tests_root', 'tests_bar', 'id', 'root_id'),
            ('tests_bar', 'tests_baz', 'id', 'parent_id')])
        self.assertEqual(self.root.get_all_join_connections(self.root_to_child2),
            [(None, 'tests_root', None, None), ('tests_root', 'tests_parent2', 'id', 'parent_id'),
            ('tests_parent2', 'tests_child2', 'id', 'parent_id')])

        self.assertEqual(self.parent1.get_all_join_connections(self.parent1_to_child1),
            [(None, 'tests_parent1', None, None), ('tests_parent1', 'tests_child1', 'id', 'parent_id')])
        self.assertEqual(self.parent1.get_all_join_connections(self.parent1_to_root),
            [(None, 'tests_parent1', None, None), ('tests_parent1', 'tests_root', 'parent_id', 'id')])
        self.assertEqual(self.parent1.get_all_join_connections(self.parent1_to_bar),
            [(None, 'tests_parent1', None, None), ('tests_parent1', 'tests_root', 'parent_id', 'id'),
            ('tests_root', 'tests_bar', 'id', 'root_id')])

        self.assertEqual(self.parent2.get_all_join_connections(self.parent2_to_child2),
            [(None, 'tests_parent2', None, None), ('tests_parent2', 'tests_child2', 'id', 'parent_id')])
        self.assertEqual(self.parent2.get_all_join_connections(self.parent2_to_baz),
            [(None, 'tests_parent2', None, None), ('tests_parent2', 'tests_child2', 'id', 'parent_id'),
            ('tests_child2', 'tests_bar', 'bar_id', 'id'), ('tests_bar', 'tests_baz', 'id', 'parent_id')])
        self.assertEqual(self.parent2.get_all_join_connections(self.parent2_to_bear),
            [(None, 'tests_parent2', None, None), ('tests_parent2', 'tests_child2', 'id', 'parent_id'),
            ('tests_child2', 'tests_bar', 'bar_id', 'id'), ('tests_bar', 'tests_baz', 'id', 'parent_id'),
            ('tests_baz', 'tests_bear_bazes', 'id', 'baz_id'), ('tests_bear_bazes', 'tests_bear', 'bear_id', 'id')])

        self.assertEqual(self.bear.get_all_join_connections(self.bear_to_bar),
            [(None, 'tests_bear', None, None), ('tests_bear', 'tests_bear_bazes', 'id', 'bear_id'),
            ('tests_bear_bazes', 'tests_baz', 'baz_id', 'id'), ('tests_baz', 'tests_bar', 'parent_id', 'id')])
        self.assertEqual(self.bear.get_all_join_connections(self.bear_to_parent1),
            [(None, 'tests_bear', None, None), ('tests_bear', 'tests_bear_bazes', 'id', 'bear_id'),
            ('tests_bear_bazes', 'tests_baz', 'baz_id', 'id'), ('tests_baz', 'tests_bar', 'parent_id', 'id'),
            ('tests_bar', 'tests_root', 'root_id', 'id'), ('tests_root', 'tests_parent1', 'id', 'parent_id')])
        self.assertEqual(self.bear.get_all_join_connections(self.bear_to_root),
            [(None, 'tests_bear', None, None), ('tests_bear', 'tests_bear_bazes', 'id', 'bear_id'),
            ('tests_bear_bazes', 'tests_baz', 'baz_id', 'id'), ('tests_baz', 'tests_bar', 'parent_id', 'id'),
            ('tests_bar', 'tests_root', 'root_id', 'id')])            