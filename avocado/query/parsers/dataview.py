from modeltree.tree import trees
from modeltree.query import ModelTreeQuerySet
from django.core.exceptions import ValidationError


SORT_DIRECTIONS = ('asc', 'desc')


def has_keys(obj, keys):
    "Check the required keys are present in `obj`"
    for key in keys:
        if key not in obj:
            return False
    return True


class Node(object):
    def __init__(self, columns=None, ordering=None, **context):
        self.concept_ids = columns or []
        self.ordering = ordering or []
        self.tree = context.pop('tree', None)
        self.context = context

    def apply(self, queryset=None, include_pk=True):
        tree = trees[self.tree]
        if queryset is None:
            queryset = tree.get_queryset()
        queryset = ModelTreeQuerySet(tree, query=queryset.query)
        if self.concept_ids:
            model_fields = []
            for f in self.fields:
                if f.lexicon:
                    model_fields.append(f.model._meta.get_field('label'))
                else:
                    model_fields.append(f.field)
            queryset = queryset.select(*model_fields, include_pk=include_pk)
        if self.ordering:
            queryset = queryset.order_by(*self.order_by)
        return queryset

    @property
    def columns(self):
        from avocado.models import DataConcept
        columns = list(DataConcept.objects.filter(pk__in=self.concept_ids))
        columns.sort(key=lambda o: self.concept_ids.index(o.pk))
        return columns

    @property
    def fields(self):
        fields = []
        for concept in self.columns:
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

            columns = list(DataConcept.objects.filter(pk__in=ids))
            columns.sort(key=lambda o: ids.index(o.pk))

            fields = []
            for concept in columns:
                fields.append(list(concept.fields.select_related('concept_fields')\
                    .order_by('concept_fields__order')))

            for i, direction in enumerate(directions):
                direction = direction.lower()
                for f in fields[i]:
                    # Special case for Lexicon-based models, order by their
                    # corresponding `order` field.
                    if f.lexicon:
                        field = f.model._meta.get_field('order')
                        qstr = tree.query_string_for_field(field)
                    else:
                        qstr = tree.query_string_for_field(f.field)
                    if direction == 'desc':
                        qstr = '-' + qstr
                    order_by.append(qstr)
        return order_by


def validate(attrs, **context):
    if not attrs:
        return

    from avocado.models import DataConcept

    columns = attrs.get('columns', [])
    ordering = attrs.get('ordering', [])

    if columns:
        if len(set(columns)) != DataConcept.objects.filter(pk__in=columns).count():
            raise ValidationError('One or more concepts do not exist')

    if ordering:
        ids, directions = zip(*ordering)

        for _dir in directions:
            if _dir.lower() not in SORT_DIRECTIONS:
                raise ValidationError('Invalid sort direction')

        if len(set(ids)) != DataConcept.objects.filter(pk__in=ids).count():
            raise ValidationError('One or more concepts do not exist')


def parse(attrs, **context):
    if not attrs:
        return Node(**context)

    columns = attrs.get('columns', None)
    ordering = attrs.get('ordering', None)
    return Node(columns, ordering, **context)
