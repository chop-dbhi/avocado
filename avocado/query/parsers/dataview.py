from modeltree.tree import trees
from modeltree.query import ModelTreeQuerySet
from django.core.exceptions import ValidationError


def has_keys(obj, keys):
    "Check the required keys are present in `obj`"
    for key in keys:
        if key not in obj:
            return False
    return True


class Node(object):
    def __init__(self, concepts=None, ordering=None, **context):
        self.concept_ids = concepts or []
        self.ordering = ordering or []
        self.tree = context.pop('tree', None)
        self.context = context

    def apply(self, queryset=None, include_pk=True):
        tree = trees[self.tree]
        if queryset is None:
            queryset = tree.get_queryset()
        queryset = ModelTreeQuerySet(tree, query=queryset.query)
        if self.concept_ids:
            queryset = queryset.select(*[f.field for f in self.fields], include_pk=include_pk)
        if self.ordering:
            queryset = queryset.order_by(*self.order_by)
        return queryset

    @property
    def concepts(self):
        from avocado.models import DataConcept
        concepts = list(DataConcept.objects.filter(pk__in=self.concept_ids))
        concepts.sort(key=lambda o: self.concept_ids.index(o.pk))
        return concepts

    @property
    def fields(self):
        fields = []
        for concept in self.concepts:
            fields.extend(list(concept.fields.select_related('concept_fields')\
                .order_by('concept_fields__order')))
        return fields

    @property
    def order_by(self):
        order_by = []
        if self.ordering:
            from avocado.models import DataConcept
            tree = trees[self.tree]
            ids, directions = zip(*self.ordering)

            concepts = list(DataConcept.objects.filter(pk__in=ids))
            concepts.sort(key=lambda o: ids.index(o.pk))

            fields = []
            for concept in self.concepts:
                fields.append(concept.fields.select_related('concept_fields')\
                    .order_by('concept_fields__order'))

            for i, direction in enumerate(directions):
                for f in fields[i]:
                    qstr = tree.query_string_for_field(f.field)
                    if direction == 'desc':
                        qstr = '-' + qstr
                    order_by.append(qstr)
        return order_by


def validate(attrs, **context):
    if not attrs:
        return
    concepts = attrs.get('concepts', [])
    ordering = attrs.get('ordering', [])

    node = Node(concepts, ordering, **context)

    if concepts and len(node.concepts) != len(concepts):
        raise ValidationError('One or more concepts do not exist')
    if ordering and len(node.order_by) != len(ordering):
        raise ValidationError('One or more concepts do not exist')


def parse(attrs, **context):
    if not attrs:
        return Node(**context)

    concepts = attrs.get('concepts', None)
    ordering = attrs.get('ordering', None)
    return Node(concepts, ordering, **context)
