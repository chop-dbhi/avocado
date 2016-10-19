from warnings import warn
from django.db import models
from avocado.core import utils
from modeltree.tree import trees
from django.db.models.query import QuerySet
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.encoding import smart_unicode

AND = 'AND'
OR = 'OR'
BRANCH_KEYS = ('children', 'type')
CONDITION_KEYS = ('operator', 'value')
COMPOSITE_KEYS = ('composite',)
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
        return True


def is_condition(obj):
    "Validates required structure for a condition node"
    if has_keys(obj, keys=CONDITION_KEYS):
        if 'field' in obj or 'id' in obj:
            return True


def is_composite(obj):
    if has_keys(obj, keys=COMPOSITE_KEYS):
        return True


class Node(object):
    condition = None
    annotations = None
    extra = None
    language = None

    def __init__(self, tree=None, **context):
        self.tree = tree
        self.context = context

    def apply(self, queryset=None, distinct=True):
        if queryset is None:
            queryset = trees[self.tree].get_queryset()
        if self.annotations:
            queryset = queryset.values('pk').annotate(**self.annotations)
        if self.condition:
            queryset = queryset.filter(self.condition)
        if self.extra:
            queryset = queryset.extra(**self.extra)
        if distinct:
            queryset = queryset.distinct()
        return queryset


class Condition(Node):
    "Contains information for a single query condition."
    def __init__(self, value, operator, id=None, field=None,
                 concept=None, **context):

        if field:
            self.field_key = field
        else:
            self.field_key = id
            warn('The "id" key has been replaced with "field"',
                 DeprecationWarning)

        self.concept_key = concept
        self.operator = operator
        self.value = value

        super(Condition, self).__init__(**context)

    @property
    def _meta(self):
        if not hasattr(self, '__meta'):
            self.__meta = self.field.translate(operator=self.operator,
                                               value=self.value,
                                               tree=self.tree, **self.context)
        return self.__meta

    @property
    def concept(self):
        if not hasattr(self, '_concept'):
            if self.concept_key:
                from avocado.models import DataConcept
                self._concept = DataConcept.objects.get(id=self.concept_key)
            else:
                self._concept = None
        return self._concept

    @property
    def field(self):
        if not hasattr(self, '_field'):
            from avocado.models import DataField
            # Parse to get into a consistent format
            field_key = utils.parse_field_key(self.field_key)

            if self.concept:
                self._field = self.concept.fields.get(**field_key)
            else:
                self._field = DataField.objects.get(**field_key)
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
                    raise TypeError('The ".extra()" method only takes list of '
                                    'dicts as keyword values')

        if self.type == OR:
            if 'where' in extra and isinstance(extra['where'], (list, tuple)):
                extra['where'] = [' OR '.join(extra['where'])]

        return extra

    @property
    def language(self):
        out = {'type': self.type.lower(), 'children': []}
        for node in self.children:
            out['children'].append(node.language)
        return out


def validate(attrs, **context):
    if not attrs:
        return None

    if type(attrs) is not dict:
        raise ValidationError('Object must be of type dict')

    enabled = attrs.pop('enabled', None)

    attrs.pop('errors', None)
    attrs.pop('warnings', None)
    errors = []
    warnings = []

    if is_composite(attrs):
        from avocado.models import DataContext
        try:
            if 'user' in context:
                cxt = DataContext.objects.get(id=attrs['composite'],
                                              user=context['user'])
            else:
                cxt = DataContext.objects.get(id=attrs['composite'])
            validate(cxt.json, **context)
            attrs['language'] = cxt.name
        except DataContext.DoesNotExist:
            enabled = False
            errors.append(u'DataContext "{0}" does not exist.'
                          .format(attrs['id']))

    elif is_condition(attrs):
        from avocado.models import DataField, DataConcept
        field_key = attrs.get('field', attrs.get('id'))
        # Parse to get into a consistent format
        field_key = utils.parse_field_key(field_key)

        try:
            if 'concept' in attrs:
                concept = DataConcept.objects.get(id=attrs['concept'])
                field = concept.fields.get(**field_key)
            else:
                field = DataField.objects.get(**field_key)
            field.validate(operator=attrs['operator'], value=attrs['value'])
            node = parse(attrs, **context)
            attrs['language'] = node.language['language']

            value = node._meta['cleaned_data']['value']
            cleaned = None

            if field.enumerable or field.simple_type == 'key':
                value_labels = field.value_labels()

                if isinstance(value, QuerySet):
                    cleaned = [{
                        'value': val.pk,
                        'label': value_labels[val.pk]
                    } for val in value]
                elif isinstance(value, (list, tuple)):
                    cleaned = []

                    for val in value:
                        if val in value_labels:
                            label = value_labels[val]
                        else:
                            label = smart_unicode(val)

                        cleaned.append({
                            'value': val,
                            'label': label
                        })
                elif isinstance(value, models.Model):
                    # Values represented by django models
                    # have only one particular label.
                    cleaned = {
                        'value': value.pk,
                        'label': value_labels[value.pk]
                    }
                else:
                    # Handle single, non-model values.
                    if value in value_labels:
                        label = value_labels[value]
                    else:
                        label = smart_unicode(value)

                    cleaned = {
                        'value': value,
                        'label': label,
                    }

            if cleaned:
                attrs['cleaned_value'] = cleaned

        except ObjectDoesNotExist:
            enabled = False
            errors.append('Field does not exist')

    elif is_branch(attrs):
        if attrs['type'] not in LOGICAL_OPERATORS:
            enabled = False
        else:
            map(lambda x: validate(x, **context), attrs['children'])
    else:
        enabled = False
        errors.append('Unknown node type')

    # If this condition was originally disabled, ensure that decision is
    # persisted
    if enabled is False:
        attrs['enabled'] = False

    if errors:
        attrs['errors'] = errors
    if warnings:
        attrs['warnings'] = warnings

    return attrs


def parse(attrs, **context):
    if not attrs or attrs.get('enabled') is False:
        node = Node(**context)
    elif is_composite(attrs):
        from avocado.models import DataContext
        if 'user' in context:
            cxt = DataContext.objects.get(id=attrs['composite'],
                                          user=context['user'])
        else:
            cxt = DataContext.objects.get(id=attrs['composite'])
        return parse(cxt.json, **context)
    elif is_condition(attrs):
        node = Condition(operator=attrs['operator'], value=attrs['value'],
                         id=attrs.get('id'), field=attrs.get('field'),
                         **context)
    else:
        node = Branch(type=attrs['type'], **context)
        node.children = map(lambda x: parse(x, **context), attrs['children'])
    return node
