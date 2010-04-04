import unittest

from columns.tests import *
from concepts.tests import *
from criteria.tests import *
from fields.tests import *
from utils.tests import *

from .models import *

class ModelTreeTestCase(unittest.TestCase):
    def setUp(self):
        self.root = ModelTree(Root)
        self.parent1 = ModelTree(Parent1)
        self.parent2 = ModelTree(Parent2)

        self.root_to_foo = self.root.path_to(Foo)
        self.root_to_baz = self.root.path_to(Baz)
        self.root_to_child2 = self.root.path_to(Child2)

        self.parent1_to_child1 = self.parent1.path_to(Child1)
        self.parent1_to_root = self.parent1.path_to(Root)
        self.parent1_to_bar = self.parent1.path_to(Bar)

        self.parent2_to_child2 = self.parent2.path_to(Child2)
        self.parent2_to_baz = self.parent2.path_to(Baz)
        self.parent2_to_bear = self.parent2.path_to(Bear)

    def test_children_length(self):
        "Test to ensure the children count are correct"
        self.failUnlessEqual(len(self.root.root_node.children), 4)
        self.failUnlessEqual(len(self.parent1.root_node.children), 2)
        self.failUnlessEqual(len(self.parent2.root_node.children), 2)

    def test_node_path_size(self):
        "Test to ensure the correct node_path size"
        self.failUnlessEqual(len(self.root_to_foo), 2)
        self.failUnlessEqual(len(self.root_to_baz), 2)        
        self.failUnlessEqual(len(self.root_to_child2), 2)

        self.failUnlessEqual(len(self.parent1_to_child1), 1)
        self.failUnlessEqual(len(self.parent1_to_root), 1)        
        self.failUnlessEqual(len(self.parent1_to_bar), 2)

        self.failUnlessEqual(len(self.parent2_to_child2), 1)
        self.failUnlessEqual(len(self.parent2_to_baz), 3)
        self.failUnlessEqual(len(self.parent2_to_bear), 4)

    def test_node_path(self):
        "Test to ensure the correct path is generated"
        self.failUnlessEqual([n.name for n in self.root_to_foo],
            ['Child3', 'Foo'])
        self.failUnlessEqual([n.name for n in self.root_to_baz],
            ['Bar', 'Baz'])
        self.failUnlessEqual([n.name for n in self.root_to_child2],
            ['Parent2', 'Child2'])

        self.failUnlessEqual([n.name for n in self.parent1_to_child1],
            ['Child1'])
        self.failUnlessEqual([n.name for n in self.parent1_to_root],
            ['Root'])
        self.failUnlessEqual([n.name for n in self.parent1_to_bar],
            ['Root', 'Bar'])

        self.failUnlessEqual([n.name for n in self.parent2_to_child2],
            ['Child2'])
        self.failUnlessEqual([n.name for n in self.parent2_to_baz],
            ['Root', 'Bar', 'Baz']) # TODO fix to go through Child2
        self.failUnlessEqual([n.name for n in self.parent2_to_bear],
            ['Root', 'Bar', 'Baz', 'Bear'])

    def test_related_name_path(self):
        "Test to ensure the correct related names are used."
        self.failUnlessEqual(self.root.related_name_path(self.root_to_foo),
            ['child3', 'foo'])
        self.failUnlessEqual(self.root.related_name_path(self.root_to_baz),
            ['bar', 'baz'])
        self.failUnlessEqual(self.root.related_name_path(self.root_to_child2),
            ['parent2', 'child2'])

        self.failUnlessEqual(self.parent1.related_name_path(self.parent1_to_child1),
            ['child1'])
        self.failUnlessEqual(self.parent1.related_name_path(self.parent1_to_root),
            ['parent'])
        self.failUnlessEqual(self.parent1.related_name_path(self.parent1_to_bar),
            ['parent', 'bar'])

        self.failUnlessEqual(self.parent2.related_name_path(self.parent2_to_child2),
            ['child2'])
        self.failUnlessEqual(self.parent2.related_name_path(self.parent2_to_baz),
            ['parent', 'bar', 'baz'])
        self.failUnlessEqual(self.parent2.related_name_path(self.parent2_to_bear),
            ['parent', 'bar', 'baz', 'bear'])

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