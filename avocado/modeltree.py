from django.db import models
from django.db.models import Q

from avocado.settings import settings

__all__ = ('ModelTreeNode', 'ModelTree', 'DEFAULT_MODELTREE')

class ModelTreeNode(object):
    def __init__(self, model, parent=None, rel_type=None, rel_is_reversed=None,
        related_name=None, accessor_name=None, depth=0):

        """Defines attributes of a `model' and the relationship to the parent
        model.

            `name' - the `model's class name

            `db_table' - the model's database table name

            `pk_field' - the model's primary key field

            `parent' - a reference to the parent ModelTreeNode

            `parent_model' - a reference to the `parent' model

            `rel_type' - denotes the _kind_ of relationship with the
            following possibilities: 'manytomany', 'onetoone', or 'foreignkey'.

            `rel_is_reversed' - denotes whether this node was derived from a
            forward relationship (an attribute lives on the parent model) or
            a reverse relationship (an attribute lives on this model).

            `related_name' - is the query string representation which is used
            when querying via the ORM.

            `accessor_name' - can be used when accessing the model object's
            attributes e.g. getattr(obj, accessor_name). this is relative to
            the parent model.

            `depth' - the depth of this node relative to the root (zero-based
            index)

            `children' - a list containing the child nodes
        """
        self.model = model
        self.name = model.__name__
        self.db_table = model._meta.db_table
        self.pk_field = model._meta.pk.column

        self.parent = parent
        self.parent_model = parent and parent.model or None
        self.rel_type = rel_type
        self.rel_is_reversed = rel_is_reversed
        self.related_name = related_name
        self.accessor_name = accessor_name
        self.depth = depth

        self.children = []

    def _get_parent_db_table(self):
        "Returns the `parent_model' database table name."
        return self.parent_model._meta.db_table
    parent_db_table = property(_get_parent_db_table)

    def _get_parent_pk_field(self):
        "Returns the `parent_model' primary key column name."
        return self.parent_model._meta.pk.column
    parent_pk_field = property(_get_parent_pk_field)

    def _get_m2m_db_table(self):
        f = getattr(self.parent_model, self.accessor_name)
        if self.rel_is_reversed:
            return f.related.field.m2m_db_table()
        else:
            return f.field.m2m_db_table()
    m2m_db_table = property(_get_m2m_db_table)

    def _get_m2m_field(self):
        f = getattr(self.parent_model, self.accessor_name)
        if self.rel_is_reversed:
            return f.related.field.m2m_column_name()
        else:
            return f.field.m2m_column_name()
    m2m_field = property(_get_m2m_field)

    def _get_m2m_reverse_field(self):
        f = getattr(self.parent_model, self.accessor_name)
        if self.rel_is_reversed:
            return f.related.field.m2m_reverse_name()
        else:
            return f.field.m2m_reverse_name()
    m2m_reverse_field = property(_get_m2m_reverse_field)

    def _get_foreignkey_field(self):
        f = getattr(self.parent_model, self.accessor_name)
        if self.rel_is_reversed:
            return f.related.field.column
        else:
            return f.field.column
    foreignkey_field = property(_get_foreignkey_field)

    def _get_join_connections(self):
        """Returns a list of connections that need to be added to a
        QuerySet object that properly joins this model and the parent.
        """
        if not hasattr(self, '_join_connections'):
            connections = []
            # setup initial FROM clause
            connections.append((None, self.parent_db_table, None, None))

            # setup two connections for m2m
            if self.rel_type == 'manytomany':
                c1 = (
                    self.parent_db_table,
                    self.m2m_db_table,
                    self.parent_pk_field,
                    self.rel_is_reversed and self.m2m_reverse_field or \
                        self.m2m_field,
                )

                c2 = (
                    self.m2m_db_table,
                    self.db_table,
                    self.rel_is_reversed and self.m2m_field or \
                        self.m2m_reverse_field,
                    self.pk_field,
                )
                connections.append(c1)
                connections.append(c2)
            else:
                c1 = (
                    self.parent_db_table,
                    self.db_table,
                    self.rel_is_reversed and self.parent_pk_field or \
                        self.foreignkey_field,
                    self.rel_is_reversed and self.foreignkey_field or \
                        self.parent_pk_field,
                )
                connections.append(c1)

            self._join_connections = connections
        return self._join_connections
    join_connections = property(_get_join_connections)

    def remove_child(self, model):
        for i,cnode in enumerate(self.children):
            if cnode.model is model:
                return self.children.pop(i)


class ModelTree(object):
    """A class to handle building and parsing a tree structure given a model.

        `root_model' - the model of interest in which everything is relatively
        defined

        `exclude' - a list of models that are not to be added to the tree
    """
    def __init__(self, root_model, exclude=()):
        if not root_model or not issubclass(root_model, models.Model):
            raise TypeError, 'root_model must be a Model subclass'
        self.root_model = root_model
        self.exclude = exclude
        self._tree_hash = {}
        self._exclude = frozenset(exclude)
        self._node_path = None

    def _filter_one2one(self, field):
        if isinstance(field, models.OneToOneField):
            return field

    def _filter_related_one2one(self, rel):
        if isinstance(rel.field, models.OneToOneField):
            return rel

    def _filter_fk(self, field):
        if isinstance(field, models.ForeignKey):
            return field

    def _filter_related_fk(self, rel):
        if isinstance(rel.field, models.ForeignKey):
            return rel

    def _add_node(self, parent, model, rel_type, rel_is_reversed, related_name,
        accessor_name, depth):
        """Adds a node to the tree only if a node of the same `model' does not
        already exist in the tree with smaller depth. If the node is added, the
        tree traversal continues finding the node's relations.
        """
        if model in self._exclude:
            return

        # check to make sure circular references don't exist
        if model not in (self.root_model, parent.parent_model):
            # don't add node if a path with a shorter depth exists
            node_hash = self._tree_hash.get(model, None)
            if not node_hash or node_hash['depth'] > depth:
                if node_hash:
                    node_hash['parent'].remove_child(model)

                node = ModelTreeNode(model, parent, rel_type, rel_is_reversed,
                    related_name, accessor_name, depth)

                self._tree_hash[model] = {'parent': parent, 'depth': depth,
                    'node': node}

                node = self._find_relations(node, depth)
                parent.children.append(node)
                del node

    def _find_relations(self, node, depth=0):
        """Finds all relations given a node.

        NOTE: the many-to-many relations are evaluated first to prevent
        'through' models being bound as a ForeignKey relationship.
        """
        depth += 1

        model_fields = node.model._meta.fields
        related_fields = node.model._meta.get_all_related_objects()

        o2o_on_model = filter(self._filter_one2one, model_fields)
        related_o2o = filter(self._filter_related_one2one, related_fields)

        fk_on_model = filter(self._filter_fk, model_fields)
        related_fk = filter(self._filter_related_fk, related_fields)

        m2m_fields = node.model._meta.many_to_many
        related_m2m = node.model._meta.get_all_related_many_to_many_objects()

        # iterate m2m relations
        for f in m2m_fields:
            kwargs = {
                'parent': node,
                'model': f.rel.to,
                'rel_type': 'manytomany',
                'rel_is_reversed': False,
                'related_name': f.name,
                'accessor_name': f.name,
                'depth': depth,
            }
            self._add_node(**kwargs)

        # iterate over related m2m fields
        for f in related_m2m:
            kwargs = {
                'parent': node,
                'model': f.model,
                'rel_type': 'manytomany',
                'rel_is_reversed': True,
                'related_name': f.field.related_query_name(),
                'accessor_name': f.get_accessor_name(),
                'depth': depth,
            }
            self._add_node(**kwargs)

        # iterate over one2one fields
        for f in o2o_on_model:
            kwargs = {
                'parent': node,
                'model': f.rel.to,
                'rel_type': 'onetoone',
                'rel_is_reversed': False,
                'related_name': f.name,
                'accessor_name': f.name,
                'depth': depth,
            }
            self._add_node(**kwargs)

        # iterate over related one2one fields
        for f in related_o2o:
            kwargs = {
                'parent': node,
                'model': f.model,
                'rel_type': 'onetoone',
                'rel_is_reversed': True,
                'related_name': f.field.related_query_name(),
                'accessor_name': f.get_accessor_name(),
                'depth': depth,
            }
            self._add_node(**kwargs)

        # iterate over fk fields
        for f in fk_on_model:
            kwargs = {
                'parent': node,
                'model': f.rel.to,
                'rel_type': 'foreignkey',
                'rel_is_reversed': False,
                'related_name': f.name,
                'accessor_name': f.name,
                'depth': depth,
            }
            self._add_node(**kwargs)

        # iterate over related foreign keys
        for f in related_fk:
            kwargs = {
                'parent': node,
                'model': f.model,
                'rel_type': 'foreignkey',
                'rel_is_reversed': True,
                'related_name': f.field.related_query_name(),
                'accessor_name': f.get_accessor_name(),
                'depth': depth,
            }
            self._add_node(**kwargs)

        return node

    def _get_root_node(self):
        "Sets the `root_node' and implicitly builds the entire tree."
        if not hasattr(self, '_root_node'):
            node = ModelTreeNode(self.root_model)
            self._root_node = self._find_relations(node)
            self._tree_hash[self.root_model] = {'parent': None, 'depth': 0,
                'node': self._root_node}
        return self._root_node
    root_node = property(_get_root_node)

    def _find_path(self, model, node, node_path=[]):
        if node.model == model:
            return node_path
        for cnode in node.children:
            mpath = self._find_path(model, cnode, node_path + [cnode])
            if mpath:
                return mpath

    def path_to(self, end_model):
        "Returns a list of nodes thats defines the path of traversal."
        return self._find_path(end_model, self.root_node)

    def path_to_with_root(self, end_model):
        """Returns a list of nodes thats defines the path of traversal
        including the root node.
        """
        return self._find_path(end_model, self.root_node, [self.root_node])

    def get_node_by_model(self, model):
        "Finds the node with the specified model."
        return self._tree_hash[model]['node']

    def query_string(self, node_path, field_name, operator=None):
        "Returns a query string given a path"
        toks = [n.related_name for n in node_path] + [field_name]
        if operator is not None:
            toks.append(operator)
        return str('__'.join(toks))

    def q(self, node_path, field_name, value, operator=None):
        "Returns a Q object."
        key = self.query_string(node_path, field_name, operator)
        return Q(**{key: value})

    def accessor_names(self, node_path):
        """Returns a list of the accessor names given a list of nodes. This is
        most useful when needing to dynamically access attributes starting from
        an instance of the `root_node' object.
        """
        return [n.accessor_name for n in node_path]

    def get_all_join_connections(self, node_path):
        """Returns a list of JOIN connections that can be manually applied to a
        QuerySet object, e.g.:

            queryset = SomeModel.objects.all()
            modeltree = ModelTree(SomeModel)
            nodes = modeltree.path_to(SomeOtherModel)
            conns = modeltree.get_all_join_connections(nodes)
            for c in conns:
                queryset.query.join(c, promote=True)

        This allows for the ORM to handle setting up the JOINs which may be
        different depending the QuerySet being altered.
        """
        connections = []
        for i,node in enumerate(node_path):
            if i == 0:
                connections.extend(node.join_connections)
            else:
                connections.extend(node.join_connections[1:])
        return connections
    
    def add_joins(self, model, queryset):
        clone = queryset._clone()
        nodes = self.path_to(model)
        conns = self.get_all_join_connections(nodes)
        for c in conns:
            clone.query.join(c, promote=True)
        return clone

    def print_path(self, node=None, depth=0):
        "Traverses the entire tree and prints a hierarchical view to stdout."
        if node is None:
            node = self.root_node
        if node:
            print '- ' * depth * 2, '"%s"' % node.name, 'at a depth of', node.depth
        if node.children:
            depth += 1
            for x in node.children:
                self.print_path(x, depth)

    def get_accessor_pairs(self, node_path):
        "Used testing purposes."
        accessor_names = self.accessor_names(node_path)
        node_path = node_path[:-1] # don't need the last item
        if len(node_path) == 0 or node_path[0] is not self.root_node:
            node_path = [self.root_node] + node_path
        else:
            accessor_names = accessor_names[1:]
        return zip(node_path, accessor_names)


if not settings.MODELTREE_MODELS:
    raise RuntimeError, 'The settings "MODELTREE_MODELS" must be set'

mods = []
for label in settings.MODELTREE_MODELS:
    app_label, model_label = label.split('.')
    mods.append(models.get_model(app_label, model_label))

DEFAULT_MODELTREE = ModelTree(mods.pop(0), exclude=mods)