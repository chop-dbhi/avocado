from modeltree.tree import trees
from django.core.exceptions import ValidationError

AND = 'AND'
OR = 'OR'
BRANCH_KEYS = ('children', 'type')
CONDITION_KEYS = ('id', 'value')
COMPOSITE_KEYS = ('id', 'composite')
LOGICAL_OPERATORS = ('and', 'or')


def has_keys(obj, keys):
    "Check the required keys are present in `obj`"
    for key in keys:
        if key not in obj:
            return False
    return True


def is_branch(obj):
    "Validates required structure for a branch node"
    if has_keys(obj, keys=BRANCH_KEYS):
        if obj['type'] not in LOGICAL_OPERATORS:
            raise ValidationError('Invalid branch operator')
        length = len(obj['children'])
        if length < 2:
            raise ValidationError('Branch must contain two or more children')
        return True


def is_condition(obj):
    "Validates required structure for a condition node"
    if has_keys(obj, keys=CONDITION_KEYS):
        return True


def is_composite(obj):
    if has_keys(obj, keys=COMPOSITE_KEYS):
        if obj['composite'] is not True:
            raise ValidationError('Composite key must be set to True.')
        return True


class Node(object):
    condition = None
    annotations = None
    extra = None
    language = None

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
    def __init__(self, id, operator, value, **context):
        self.id = id
        self.operator = operator
        self.value = value
        super(Condition, self).__init__(**context)

    @property
    def _meta(self):
        if not hasattr(self, '__meta'):
            self.__meta = self.field.translate(operator=self.operator,
                value=self.value, tree=self.tree, **self.context)
        return self.__meta

    @property
    def field(self):
        if not hasattr(self, '_field'):
            from avocado.models import DataField
            self._field = DataField.objects.get(pk=self.id)
        return self._field

    @property
    def condition(self):
        return self._meta['query_modifiers'].get('condition', None)

    @property
    def annotations(self):
        return self._meta['query_modifiers'].get('annotations', None)

    @property
    def extra(self):
        return self._meta['query_modifiers'].get('extra', None)

    @property
    def language(self):
        meta = self._meta.copy()
        meta.pop('query_modifiers')
        cleaned = meta.pop('cleaned_data')
        meta['language'] = cleaned['language']
        return meta


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
    def language(self):
        out = {'type': self.type.lower(), 'children': []}
        for node in self.children:
            out['children'].append(node.language)
        return out


def validate(attrs, **context):
    if type(attrs) is not dict:
        raise ValidationError('Object must be of type dict')
    if not attrs:
        return
    if is_composite(attrs):
        from avocado.models import DataContext
        try:
            if 'user' in context:
                cxt = DataContext.objects.get(id=attrs['id'], user=context['user'])
            else:
                cxt = DataContext.objects.get(id=attrs['id'])
        except DataContext.DoesNotExist:
            raise ValidationError('DataContext "{}" does not exist.'.format(attrs['id']))
        validate(cxt.json, **context)
    elif is_condition(attrs):
        from avocado.models import DataField
        try:
            datafield = DataField.objects.get_by_natural_key(attrs['id'])
        except DataField.DoesNotExist, e:
            raise ValidationError(e.message)
        datafield.validate(operator=attrs['operator'], value=attrs['value'])
    elif is_branch(attrs):
        map(lambda x: validate(x), attrs['children'])
    else:
        raise ValidationError('Object neither a branch nor condition: {}'.format(attrs))


def parse(attrs, **context):
    if not attrs:
        node = Node(**context)
    elif is_composite(attrs):
        from avocado.models import DataContext
        if 'user' in context:
            cxt = DataContext.objects.get(id=attrs['id'], user=context['user'])
        else:
            cxt = DataContext.objects.get(id=attrs['id'])
        return parse(cxt.json, **context)
    elif is_condition(attrs):
        node = Condition(attrs['id'], attrs.get('operator', None), attrs['value'], **context)
    else:
        node = Branch(attrs['type'], **context)
        node.children = map(lambda x: parse(x, **context), attrs['children'])
    return node
