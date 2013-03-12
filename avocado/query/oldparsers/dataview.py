import warnings
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
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

    def _get_concepts(self, ids):
        "Returns an ordered list of concepts based on `ids`."
        from avocado.models import DataConcept
        if not ids:
            return []
        concepts = list(DataConcept.objects.filter(pk__in=ids))
        concepts.sort(key=lambda o: ids.index(o.pk))
        return concepts

    def _get_fields_for_concepts(self, ids):
        "Returns an ordered list of fields for concept `ids`."
        from avocado.models import DataConceptField
        if not ids:
            return OrderedDict()
        # Concept fields that are sorted by concept then order, but are not
        # in the original order defined in `ids`
        cfields = list(DataConceptField.objects.filter(concept__pk__in=ids)\
            .select_related()\
            .order_by('concept', 'order'))

        # Order concept fields relative to `ids`
        cfields.sort(key=lambda o: ids.index(o.concept.pk))

        # Construct an ordered dict of fields by their concept
        groups = OrderedDict()
        for cf in cfields:
            pk = cf.concept.pk
            if pk not in groups:
                groups[pk] = []
            groups[pk].append(cf.field)
        return groups

    def _get_select(self, distinct):
        # Apply all fields to the query to ensure ordering get applied.
        # Django removes ORDER BY statements if column is not present in
        # SELECT since it will cause a SQL error. This ensures the ordering
        # is applied at the SQL level. The caveat here is that the rows
        # returned will include this extra data. The exporter classes handle
        # this by removing redundant rows relative to the *original* columns.
        ids = list(self.concept_ids)
        if self.ordering and distinct:
            ids += list(zip(*self.ordering)[0])

        # Flatten the grouped fields
        fields = [i for l in self._get_fields_for_concepts(ids).values() for i in l]

        model_fields = []

        for f in fields:
            if f.lexicon:
                model_fields.append(f.model._meta.get_field('label'))
            else:
                model_fields.append(f.field)
        return model_fields

    def _get_order_by(self):
        "Returns directional lookups to be unpacked in `QuerySet.order_by`."
        order_by = []

        if self.ordering:
            tree = trees[self.tree]
            ids, directions = zip(*self.ordering)
            groups = self._get_fields_for_concepts(ids)

            for pk, direction in self.ordering:
                for f in groups[pk]:
                    # Special case for Lexicon-based models, order by their
                    # model-defined `order` field.
                    if f.lexicon:
                        field = f.model._meta.get_field('order')
                        lookup = tree.query_string_for_field(field)
                    else:
                        lookup = tree.query_string_for_field(f.field)

                    if direction.lower() == 'desc':
                        order_by.append('-' + lookup)
                    else:
                        order_by.append(lookup)

        return order_by

    # Primary method for apply this view to a QuerySet
    def apply(self, queryset=None, include_pk=True):
        tree = trees[self.tree]
        if queryset is None:
            queryset = tree.get_queryset()

        # Convert to a ModelTreeQuerySet for the `select()` method
        queryset = ModelTreeQuerySet(tree, query=queryset.query)

        # Set model fields for `select()` method
        select = self._get_select(queryset.query.distinct)
        queryset = queryset.select(*select, include_pk=include_pk)

        # Set the order by on the QuerySet
        order_by = self._get_order_by()
        if order_by:
            queryset = queryset.order_by(*order_by)

        return queryset

    # Additional public methods for general use and interrogation
    def get_concepts_for_select(self):
        return self._get_concepts(self.concept_ids)

    def get_fields_for_select(self):
        return self._get_fields_for_concepts(self.concept_ids)

    def get_concepts_for_order_by(self):
        ids = []
        if self.ordering:
            ids = zip(*self.ordering)[0]
        return self._get_concepts(ids)

    def get_fields_for_order_by(self):
        ids = []
        if self.ordering:
            ids = zip(*self.ordering)[0]
        return self._get_fields_for_concepts(ids)

    @property
    def columns(self):
        warnings.warn('This property has been deprecated, used '
            'get_concepts_for_select() instead', DeprecationWarning)
        return self.get_concepts_for_select()


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
