from modeltree.tree import trees
from . import datacontext as datacontext_parser
from . import dataview as dataview_parser

class Node(object):
    datacontext_node = None 
    dataview_node = None

    def __init__(self, datacontext_node=None, dataview_node=None, **context):
        self.datacontext_node = datacontext_node
        self.dataview_node = dataview_node

    def apply(self, queryset=None, distinct=True, include_pk=True):
        if self.dataview_node:
            queryset = self.dataview_node.apply(queryset, include_pk)
        
        if self.datacontext_node:
            queryset = self.datacontext_node.apply(queryset, distinct)
        
        return queryset


def validate(attrs, **context):
    if not attrs:
        return

    datacontext_attrs = attrs.get('context', None)
    dataview_attrs = attrs.get('view', None)

    ret_attrs = {}
    
    if datacontext_attrs:
       ret_attrs['context'] = datacontext_parser.validate(datacontext_attrs, 
               **context)

    if dataview_attrs:
        ret_attrs['view'] = dataview_parser.validate(dataview_attrs, **context)    

    return ret_attrs

def parse(attrs, tree=None, **context):
    if not attrs:
        return Node(**context)

    datacontext_attrs = attrs.get('context', None)
    if datacontext_attrs:
        datacontext_node = datacontext_parser.parse(datacontext_attrs, 
                tree=tree, **context)
    else:
        datacontext_node = None

    dataview_attrs = attrs.get('view', None)
    if dataview_attrs:
        dataview_node = dataview_parser.parse(dataview_attrs, tree=tree, 
                **context)
    else:
        dataview_node = None

    return Node(datacontext_node, dataview_node, **context)
