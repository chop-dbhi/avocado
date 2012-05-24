from modeltree.tree import trees
from django.core.exceptions import ValidationError

AND = 'AND'
OR = 'OR'
BRANCH_KEYS = ('children', 'type')
CONDITION_KEYS = ('id', 'value')
LOGICAL_OPERATORS = ('and', 'or')


def has_keys(obj, keys):
    "Check the required keys are present in `obj`"
    for key in keys:
        if key not in obj:
            return False
    return True


def parse_branch(obj):
    "Validates required structure for a branch node"
    if has_keys(obj, keys=BRANCH_KEYS):
        if obj['type'] not in LOGICAL_OPERATORS:
            raise ValidationError('Invalid logical operator between conditions')
        length = len(obj['children'])
        if length < 2:
            raise ValidationError('Invalid format. Branch node must contain two or more conditions')
        return True


def parse_condition(obj):
    "Validates required structure for a condition node"
    if has_keys(obj, keys=CONDITION_KEYS):
        return True


class Node(object):
    condition = None
    annotations = None
    extra = None
    text = None

    def __init__(self, **context):
        self.tree = context.pop('tree', None)
        self.context = context

    def apply(self, queryset=None):
        if queryset is None:
            queryset = trees[self.tree].get_queryset()
        if self.annotations:
            queryset = queryset.values('pk').annotate(**self.annotations)
        if self.condition:
            queryset = queryset.filter(self.condition)
        if self.extra:
            queryset = queryset.extra(**self.extra)
        return queryset


class Condition(Node):
    "Contains information for a single query condition."
    def __init__(self, id, value, operator=None, **context):
        self.id = id
        self.value = value
        self.operator = operator
        super(Condition, self).__init__(**context)

    @property
    def _meta(self, tree=None):
        if not hasattr(self, '__meta'):
            self.__meta = self.field.translate(self.operator, self.value,
                tree=self.tree, **self.context)
        return self.__meta

    @property
    def field(self):
        if not hasattr(self, '_field'):
            from avocado.models import DataField
            self._field = DataField.objects.get(pk=self.id)
        return self._field

    @property
    def condition(self):
        return self._meta.get('condition', None)

    @property
    def annotations(self):
        return self._meta.get('annotations', None)

    @property
    def extra(self):
        return self._meta.get('extra', None)

    @property
    def text(self):
        operator = self._meta['cleaned_data']['operator']
        # The original value is used here to prevent representing a different
        # value from what the client had submitted. This text has no impact
        # on the stored 'cleaned' data structure
        value = self._meta['raw_data']['value']
        return {'conditions': [u'{} {}'.format(self.field.name, operator.text(value))]}


class Branch(Node):
    "Provides a logical relationship between it's children."
    def __init__(self, type, **context):
        self.type = (type.upper() == AND) and AND or OR
        self.children = []
        super(Branch, self).__init__(**context)

    def _combine(self, q1, q2):
        if self.type.upper() == OR:
            return q1 | q2
        return q1 & q2

    @property
    def condition(self):
        if not hasattr(self, '_condition'):
            condition = None
            for node in self.children:
                if node.condition:
                    if condition:
                        condition = self._combine(node.condition, condition)
                    else:
                        condition = node.condition
            self._condition = condition
        return self._condition

    @property
    def annotations(self):
        if not hasattr(self, '_annotations'):
            self._annotations = {}
            for node in self.children:
                if node.annotations:
                    self._annotations.update(node.annotations)
        return self._annotations

    @property
    def extra(self):
        extra = {}
        for node in self.children:
            if not node.extra:
                continue
            for key, value in node.extra.items():
                _type = type(value)
                # Initialize an empty container for the value type..
                extra.setdefault(key, _type())
                if _type is list:
                    current = extra[key][:]
                    [extra[key].append(x) for x in value if x not in current]
                elif _type is dict:
                    extra[key].update(value)
                else:
                    raise TypeError('The `.extra()` method only takes list of dicts as keyword values')
        return extra

    @property
    def text(self):
        text = {'type': self.type.lower(), 'conditions': []}
        for node in self.children:
            t = node.text
            # Flatten if nested conditions are also AND's
            if 'type' not in t or t['type'] == self.type.lower():
                text['conditions'].extend(t['conditions'])
            else:
                text['conditions'].append(t['conditions'])
        return text


def validate(attrs):
    if type(attrs) is not dict:
        raise ValidationError('Object must be of type dict')
    if parse_condition(attrs):
        from avocado.models import DataField
        try:
            datafield = DataField.objects.get_by_natural_key(attrs.pop('id'))
        except DataField.DoesNotExist, e:
            raise ValidationError(e.message)
        datafield.validate(**attrs)
    elif parse_branch(attrs):
        map(lambda x: validate(x), attrs['children'])
    else:
        raise ValidationError('Object neither a branch nor condition: {0}'.format(attrs))


def parse(attrs, **context):
    if not attrs:
        node = Node(**context)
    elif parse_condition(attrs):
        node = Condition(attrs['id'], attrs['value'],
            attrs.get('operator', None), **context)
    else:
        node = Branch(attrs['type'], **context)
        node.children = map(lambda x: parse(x, **context), attrs['children'])
    return node
