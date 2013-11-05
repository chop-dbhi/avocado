from . import datacontext as datacontext_parser
from . import dataview as dataview_parser


class Node(object):
    datacontext_node = None
    dataview_node = None

    def __init__(self, datacontext_node=None, dataview_node=None, **context):
        self.datacontext_node = datacontext_node
        self.dataview_node = dataview_node

    def apply(self, queryset=None, distinct=True, include_pk=True):
        queryset = \
            self.datacontext_node.apply(queryset=queryset, distinct=distinct)
        return \
            self.dataview_node.apply(queryset=queryset, include_pk=include_pk)


def validate(attrs, **context):
    if not attrs:
        return

    datacontext_attrs = attrs.get('context', {})
    dataview_attrs = attrs.get('view', {})

    ret_attrs = {}

    ret_attrs['context'] = \
        datacontext_parser.validate(datacontext_attrs, **context)

    ret_attrs['view'] = dataview_parser.validate(dataview_attrs, **context)

    return ret_attrs


def parse(attrs, tree=None, **context):
    if not attrs:
        return Node(**context)

    datacontext_attrs = attrs.get('context', {})
    datacontext_node = \
        datacontext_parser.parse(datacontext_attrs, tree=tree, **context)

    dataview_attrs = attrs.get('view', {})
    dataview_node = \
        dataview_parser.parse(dataview_attrs, tree=tree, **context)

    return Node(datacontext_node, dataview_node, **context)
