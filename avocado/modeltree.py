import inspect

from django.db import models
from django.db.models import Q
from django.core.exceptions import ImproperlyConfigured

from avocado.conf import settings

__all__ = ('ModelTree',)

DEFAULT_MODELTREE_ALIAS = 'default'

class ModelTreeNode(object):
    def __init__(self, model, parent=None, rel_type=None, rel_reversed=None,
        related_name=None, accessor_name=None, depth=0):

        """Defines attributes of a `model' and the relationship to the parent
        model.

            `name' - the `model's class name

            `db_table' - the model's database table name

            `pk_field' - the model's primary key field

            `parent' - a reference to the parent ModelTreeNode

            `parent_model' - a reference to the `parent' model, since it may be
            None

            `rel_type' - denotes the _kind_ of relationship with the
            following possibilities: 'manytomany', 'onetoone', or 'foreignkey'.

            `rel_reversed' - denotes whether this node was derived from a
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
        self.rel_reversed = rel_reversed
        self.related_name = related_name
        self.accessor_name = accessor_name
        self.depth = depth

        self.children = []

    def __str__(self):
        return '%s via %s' % (self.name, self.parent_model.__name__)

    def _get_m2m_db_table(self):
        f = getattr(self.parent_model, self.accessor_name)
        if self.rel_reversed:
            return f.related.field.m2m_db_table()
        else:
            return f.field.m2m_db_table()
    m2m_db_table = property(_get_m2m_db_table)

    def _get_m2m_field(self):
        f = getattr(self.parent_model, self.accessor_name)
        if self.rel_reversed:
            return f.related.field.m2m_column_name()
        else:
            return f.field.m2m_column_name()
    m2m_field = property(_get_m2m_field)

    def _get_m2m_reverse_field(self):
        f = getattr(self.parent_model, self.accessor_name)
        if self.rel_reversed:
            return f.related.field.m2m_reverse_name()
        else:
            return f.field.m2m_reverse_name()
    m2m_reverse_field = property(_get_m2m_reverse_field)

    def _get_foreignkey_field(self):
        f = getattr(self.parent_model, self.accessor_name)
        if self.rel_reversed:
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
            connections.append((None, self.parent.db_table, None, None))

            # setup two connections for m2m
            if self.rel_type == 'manytomany':
                c1 = (
                    self.parent.db_table,
                    self.m2m_db_table,
                    self.parent.pk_field,
                    self.rel_reversed and self.m2m_reverse_field or \
                        self.m2m_field,
                )

                c2 = (
                    self.m2m_db_table,
                    self.db_table,
                    self.rel_reversed and self.m2m_field or \
                        self.m2m_reverse_field,
                    self.pk_field,
                )
                connections.append(c1)
                connections.append(c2)
            else:
                c1 = (
                    self.parent.db_table,
                    self.db_table,
                    self.rel_reversed and self.parent.pk_field or \
                        self.foreignkey_field,
                    self.rel_reversed and self.foreignkey_field or \
                        self.parent.pk_field,
                )
                connections.append(c1)

            self._join_connections = connections
        return self._join_connections
    join_connections = property(_get_join_connections)

    def remove_child(self, model):
        for i, cnode in enumerate(self.children):
            if cnode.model is model:
                return self.children.pop(i)


class ModelTree(object):
    """A class to handle building and parsing a tree structure given a model.

        `root_model' - the model of interest in which everything is relatively
        defined

        `exclude' - a list of models that are not to be added to the tree
    """
    def __init__(self, root_model, exclude=(), routes=()):
        self.root_model = self._get_model(root_model)
        self.exclude = map(self._get_model, exclude)

        self._rts, self._tos = self._build_routes(routes)
        self._tree_hash = {}

    def check(self, queryset):
        if queryset.model is self.root_model:
            return True
        return False

    def _get_model(self, label):
        # model class
        if inspect.isclass(label) and issubclass(label, models.Model):
            return label
        # passed as a label string
        elif isinstance(label, basestring):
            model = None
            if '.' in label:
                app_label, model_label = label.lower().split('.')
                model = models.get_model(app_label, model_label)
            if model:
                return model
        raise ImproperlyConfigured('The model "{0}" could not be found'.format(label))

    def _build_routes(self, routes):
        """
        Routes provide a means of specifying JOINs between two tables.

        The minimum information necessary to define an explicit JOIN is as
        follows:

            'from_label' - defines the model on the right side of the join
            'to_label' - defines the model on the left side of the join
            'join_field' - defines the field in which the join will occur
            'symmetrical' - defines whether the same join will be constructed
                if the 'from_model' and 'to_model' are reversed
        """
        rts = {}
        tos = {}

        for route in routes:
            # unpack
            from_label, to_label, join_field, symmetrical = route

            # get models
            from_model = self._get_model(from_label)
            to_model = self._get_model(to_label)

            # get field
            if join_field is not None:
                model_name, field_name = join_field.split('.')
                model_name = model_name.lower()

                if model_name == from_model.__name__.lower():
                    field = from_model._meta.get_field_by_name(field_name)[0]
                elif model_name == to_model.__name__.lower():
                    field = to_model._meta.get_field_by_name(field_name)[0]
                else:
                    raise TypeError, 'model for join_field, "%s", does not match' % field_name

                if field is None:
                    raise TypeError, 'field "%s" not found'
            else:
                field = None

            if field:
                rts[(from_model, to_model)] = field
                if symmetrical:
                    rts[(to_model, from_model)] = field
            else:
                tos[to_model] = from_model

        return rts, tos


    def _filter_one2one(self, field):
        """Tests if this field is a OneToOneField. If a route exists for this
        field's model and it's target model, ensure this is the field that
        should be used to join the the two tables.
        """
        if isinstance(field, models.OneToOneField):
            # route has been defined with a specific field required
            tup = (field.model, field.rel.to)
            # skip if not the correct field
            if self._rts.has_key(tup) and self._rts.get(tup) is not field:
                return
            return field

    def _filter_related_one2one(self, rel):
        """Tests if this RelatedObject represents a OneToOneField. If a route
        exists for this field's model and it's target model, ensure this is
        the field that should be used to join the the two tables.
        """
        field = rel.field
        if isinstance(field, models.OneToOneField):
            # route has been defined with a specific field required
            tup = (rel.model, field.model)
            # skip if not the correct field
            if self._rts.has_key(tup) and self._rts.get(tup) is not field:
                return
            return rel

    def _filter_fk(self, field):
        """Tests if this field is a ForeignKey. If a route exists for this
        field's model and it's target model, ensure this is the field that
        should be used to join the the two tables.
        """
        if isinstance(field, models.ForeignKey):
            # route has been defined with a specific field required
            tup = (field.model, field.rel.to)
            # skip if not the correct field
            if self._rts.has_key(tup) and self._rts.get(tup) is not field:
                return
            return field

    def _filter_related_fk(self, rel):
        """Tests if this RelatedObject represents a ForeignKey. If a route
        exists for this field's model and it's target model, ensure this is
        the field that should be used to join the the two tables.
        """
        field = rel.field
        if isinstance(field, models.ForeignKey):
            # route has been defined with a specific field required
            tup = (rel.model, field.model)
            # skip if not the correct field
            if self._rts.has_key(tup) and self._rts.get(tup) is not field:
                return
            return rel

    def _filter_m2m(self, field):
        """Tests if this field is a ManyToManyField. If a route exists for this
        field's model and it's target model, ensure this is the field that
        should be used to join the the two tables.
        """
        if isinstance(field, models.ManyToManyField):
            # route has been defined with a specific field required
            tup = (field.model, field.rel.to)
            # skip if not the correct field
            if self._rts.has_key(tup) and self._rts.get(tup) is not field:
                return
            return field

    def _filter_related_m2m(self, rel):
        """Tests if this RelatedObject represents a ManyToManyField. If a route
        exists for this field's model and it's target model, ensure this is
        the field that should be used to join the the two tables.
        """
        field = rel.field
        if isinstance(field, models.ManyToManyField):
            # route has been defined with a specific field required
            tup = (rel.model, field.model)
            # skip if not the correct field
            if self._rts.has_key(tup) and self._rts.get(tup) is not field:
                return
            return rel

    def _add_node(self, parent, model, rel_type, rel_reversed, related_name,
        accessor_name, depth):
        """Adds a node to the tree only if a node of the same `model' does not
        already exist in the tree with smaller depth. If the node is added, the
        tree traversal continues finding the node's relations.

        Conditions in which the node will fail to be added:

            - the model is excluded completely
            - the model is going back the same path it came from
            - the model is circling back to the root_model
            - the model does not come from the parent.model (via _tos)
        """
        exclude = set(self.exclude + [parent.parent_model, self.root_model])

        # ignore excluded models and prevent circular paths
        if model in exclude:
            return

        # if a route exists, only allow the model to be added if coming from the
        # specified parent.model
        if self._tos.has_key(model) and self._tos.get(model) is not parent.model:
            return

        node_hash = self._tree_hash.get(model, None)

        # don't add node if a path with a shorter depth exists. this is applied
        # after the correct join has been determined. generally if a route is
        # defined for relation, this will never be an issue since there would
        # only be one path available. if a route is not defined, the shorter
        # path will be found
        if not node_hash or node_hash['depth'] > depth:
            if node_hash:
                node_hash['parent'].remove_child(model)

            node = ModelTreeNode(model, parent, rel_type, rel_reversed,
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

        model = node.model

        # determine relational fields to determine paths
        forward_fields = model._meta.fields
        reverse_fields = model._meta.get_all_related_objects()

        forward_o2o = filter(self._filter_one2one, forward_fields)
        reverse_o2o = filter(self._filter_related_one2one, reverse_fields)

        forward_fk = filter(self._filter_fk, forward_fields)
        reverse_fk = filter(self._filter_related_fk, reverse_fields)

        forward_m2m = filter(self._filter_m2m, model._meta.many_to_many)
        reverse_m2m = filter(self._filter_related_m2m, model._meta.get_all_related_many_to_many_objects())

        # iterate m2m relations
        for f in forward_m2m:
            kwargs = {
                'parent': node,
                'model': f.rel.to,
                'rel_type': 'manytomany',
                'rel_reversed': False,
                'related_name': f.name,
                'accessor_name': f.name,
                'depth': depth,
            }
            self._add_node(**kwargs)

        # iterate over related m2m fields
        for r in reverse_m2m:
            kwargs = {
                'parent': node,
                'model': r.model,
                'rel_type': 'manytomany',
                'rel_reversed': True,
                'related_name': r.field.related_query_name(),
                'accessor_name': r.get_accessor_name(),
                'depth': depth,
            }
            self._add_node(**kwargs)

        # iterate over one2one fields
        for f in forward_o2o:
            kwargs = {
                'parent': node,
                'model': f.rel.to,
                'rel_type': 'onetoone',
                'rel_reversed': False,
                'related_name': f.name,
                'accessor_name': f.name,
                'depth': depth,
            }
            self._add_node(**kwargs)

        # iterate over related one2one fields
        for r in reverse_o2o:
            kwargs = {
                'parent': node,
                'model': r.model,
                'rel_type': 'onetoone',
                'rel_reversed': True,
                'related_name': r.field.related_query_name(),
                'accessor_name': r.get_accessor_name(),
                'depth': depth,
            }
            self._add_node(**kwargs)

        # iterate over fk fields
        for f in forward_fk:
            kwargs = {
                'parent': node,
                'model': f.rel.to,
                'rel_type': 'foreignkey',
                'rel_reversed': False,
                'related_name': f.name,
                'accessor_name': f.name,
                'depth': depth,
            }
            self._add_node(**kwargs)

        # iterate over related foreign keys
        for r in reverse_fk:
            kwargs = {
                'parent': node,
                'model': r.model,
                'rel_type': 'foreignkey',
                'rel_reversed': True,
                'related_name': r.field.related_query_name(),
                'accessor_name': r.get_accessor_name(),
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

    def path_to(self, model):
        "Returns a list of nodes thats defines the path of traversal."
        model = self._get_model(model)
        return self._find_path(model, self.root_node)

    def path_to_with_root(self, model):
        """Returns a list of nodes thats defines the path of traversal
        including the root node.
        """
        model = self._get_model(model)
        return self._find_path(model, self.root_node, [self.root_node])

    def get_node_by_model(self, model):
        "Finds the node with the specified model."
        model = self._get_model(model)
        if not self._tree_hash:
            self.root_node
        val = self._tree_hash.get(model, None)
        if val is None:
            return
        return val['node']

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

    def add_joins(self, model, queryset, **kwargs):
        model = self._get_model(model)

        clone = queryset._clone()
        nodes = self.path_to(model)
        conns = self.get_all_join_connections(nodes)
        for c in conns:
            clone.query.join(c, **kwargs)
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
        "Used for testing purposes."
        accessor_names = self.accessor_names(node_path)
        node_path = node_path[:-1] # don't need the last item
        if len(node_path) == 0 or node_path[0] is not self.root_node:
            node_path = [self.root_node] + node_path
        else:
            accessor_names = accessor_names[1:]
        return zip(node_path, accessor_names)

    def get_queryset(self):
        "Returns a QuerySet relative to the ``root_model``."
        return self.root_model.objects.all()


class LazyModelTree(object):
    def __init__(self, modeltrees):
        self.modeltrees = modeltrees
        self._modeltrees = {}

    def __getitem__(self, alias):
        if not self.modeltrees:
            raise ImproperlyConfigured, 'You must at least specify the "%s" ' \
                'modeltree config' % DEFAULT_MODELTREE_ALIAS

        if alias not in self._modeltrees:
            try:
                kwargs = self.modeltrees[alias]
            except KeyError:
                raise KeyError, 'No modeltree settings defined for "%s"' % alias

            self._modeltrees[alias] = ModelTree(**kwargs)
        return self._modeltrees[alias]

trees = LazyModelTree(settings.MODELTREES)
