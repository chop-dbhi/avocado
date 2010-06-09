from django.db import models

class ModelTreeNode(object):
    def __init__(self, model, parent=None, rel_type=None, rel_is_reversed=None,
        related_name=None, accessor_name=None, depth=None):

        """Defines helper attributes of a `model` and the relationship to the
        parent model. The model `name` is captured for convenience and a
        reference to the `parent` node is kept to allow traversal back up
        the tree.

        `rel_type` denotes the _kind_ of relationship which the
        following possibilities: 'manytomany', 'onetoone', or 'foreignkey'.

        `related_name` is the query string representation, i.e. the actual
        field name as know by the parent model.

        `accessor_name` can be used when accessing the model object's
        attributes e.g. getattr(obj, accessor_name). this is relative to the
        parent model.

        `db_table` is a simple reference to the model's database table name.

        `pk_field` is the model's primary key field.

        `children` is a list containing the child nodes.
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
        return self.parent_model._meta.db_table
    parent_db_table = property(_get_parent_db_table)

    def _get_parent_pk_field(self):
        return self.parent_model._meta.pk.column
    parent_pk_field = property(_get_parent_pk_field)

    def _get_m2m_db_table(self):
        if not self.rel_is_reversed:
            f = getattr(self.parent_model, self.related_name).field
        else:
            f = getattr(self.parent_model, self.accessor_name).related.field
        return f.m2m_db_table()
    m2m_db_table = property(_get_m2m_db_table)

    def _get_m2m_field(self):
        if not self.rel_is_reversed:
            f = getattr(self.parent_model, self.related_name).field
        else:
            f = getattr(self.parent_model, self.accessor_name).related.field
            return f.m2m_column_name()
    m2m_field = property(_get_m2m_field)

    def _get_m2m_reverse_field(self):
        if self.rel_is_reversed:
            f = getattr(self.parent_model, self.related_name).field
        else:
            f = getattr(self.parent_model, self.accessor_name).related.field
        return f.m2m_reverse_name()
    m2m_reverse_field = property(_get_m2m_reverse_field)

    def _get_foreignkey_field(self):
        if not self.rel_is_reversed:
            f = getattr(self.parent_model, self.related_name).field
        else:
            f = getattr(self.parent_model, self.accessor_name).related.field
        return f.column
    foreignkey_field = property(_get_foreignkey_field)
    
    def _get_join_connections(self):
        """Returns a list of connections that need to be added to a
        queryset that properly joins this model and the parent.
        """
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

        return connections
    join_connections = property(_get_join_connections)

    def remove_child(self, model):
        for i,x in enumerate(self.children):
            if x.model is model:
                return self.children.pop(i)


class ModelTree(object):
    """A class to handle building and parsing a tree strucutre based on a
    model.

    `root_model' defines the model of interest in which everything is
    relatively defined.

    `exclude' is propagates through to the `ModelTree`
    class where it prevents certain models from being added to the tree.
    """
    def __init__(self, root_model, exclude=()):
        self.root_model = root_model
        self._path_depth = {}
        self._exclude = frozenset(exclude)
        self._root_node = None
        self._node_path = None

    def _get_root_node(self):
        if self._root_node is None:
            node = ModelTreeNode(self.root_model, depth=0)
            self._root_node = self._find_relations(node)
        return self._root_node
    root_node = property(_get_root_node)

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
        
        if model in self._exclude:
            return
        
        if model not in (self.root_model, parent.parent_model):
            # don't add node if a path with a shorter depth exists
            path_depth = self._path_depth.get(model, None)
            if not path_depth or path_depth[1] > depth:
                if path_depth:
                    path_depth[0].remove_child(model)

                node = ModelTreeNode(model, parent, rel_type, rel_is_reversed,
                    related_name, accessor_name, depth)
                
                self._path_depth[model] = (parent, depth)
                
                node = self._find_relations(node, depth)
                parent.children.append(node)
                del node

    def _find_relations(self, node, depth=0):
        """Finds all relations with the `node` model.

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

    def _find_path(self, node, model, node_path=[]):
        if node.model == model:
            return node_path
        for c in node.children:
            mpath = self._find_path(c, model, node_path + [c])
            if mpath:
                return mpath

    def print_path(self, node=None, depth=0):
        if node is None:
            node = self.root_node
        if node:
            print '- ' * depth * 2, '"%s"' % node.name, 'at a depth of', node.depth
        if node.children:
            depth += 1
            for x in node.children:
                self.print_path(x, depth)
    
    def path_to(self, end_model):
        return self._find_path(self.root_node, end_model)

    def path_to_with_root(self, end_model):
        return self._find_path(self.root_node, end_model, [self.root_node])

    def related_name_path(self, node_path):
        return [n.related_name for n in node_path]

    def accessor_name_path(self, node_path):
        return [n.accessor_name for n in node_path]
    
    def get_accessor_pairs(self, node_path):
        accessor_names = self.accessor_name_path(node_path)
        node_path = node_path[:-1] # don't need the last item
        if len(node_path) == 0 or node_path[0] is not self.root_node:
            node_path = [self.root_node] + node_path
        else:
            accessor_names = accessor_names[1:]
        return zip(node_path, accessor_names)

    def get_all_join_connections(self, node_path):
        connections = []
        for i,n in enumerate(node_path):
            if i == 0:
                connections.extend(n.join_connections)
            else:
                connections.extend(n.join_connections[1:])
        return connections
