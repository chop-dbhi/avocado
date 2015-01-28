from warnings import warn
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from modeltree.tree import trees


SORT_DIRECTIONS = ('asc', 'desc')


class Node(object):
    def __init__(self, facets=None, **context):
        self.facets = facets or []
        self.tree = context.pop('tree', None)
        self.context = context

    @property
    def concept_ids(self):
        ids = []

        for facet in self.facets:
            if facet.get('enabled') is False:
                continue

            if facet.get('visible') is False:
                continue

            ids.append(facet['concept'])

        return ids

    @property
    def ordering(self):
        ids = []
        length = len(self.facets)

        for facet in self.facets:
            if facet.get('enabled') is False:
                continue

            if facet.get('sort') in SORT_DIRECTIONS:
                # If sort is not defined, default to length of facets
                ids.append((
                    facet.get('sort_index', length),
                    facet['concept'],
                    facet['sort'],
                ))

        # Sort relative to sort index
        ids.sort(key=lambda x: x[0])
        # Return only the concept id and sort direction
        return [(c, s) for i, c, s in ids]

    def _get_concepts(self, ids):
        "Returns an ordered list of concepts based on `ids`."
        if not ids:
            return []

        from avocado.models import DataConcept

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
        cfields = list(DataConceptField.objects.filter(concept__pk__in=ids)
                       .select_related()
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
        ordering = self.ordering

        if ordering and distinct:
            ids += list(zip(*ordering)[0])

        # Flatten the grouped fields
        fields = [i for l in self._get_fields_for_concepts(ids).values()
                  for i in l]

        model_fields = []

        for f in fields:
            model_fields.append((f.model, f.label_field))

        return model_fields

    def _get_order_by(self):
        "Returns directional lookups to be unpacked in `QuerySet.order_by`."
        order_by = []
        ordering = self.ordering

        if ordering:
            tree = trees[self.tree]
            ids, directions = zip(*ordering)
            groups = self._get_fields_for_concepts(ids)

            for pk, direction in ordering:
                for f in groups[pk]:
                    lookup = tree.query_string_for_field(f.order_field,
                                                         model=f.model)

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

        # Add the fields to the queryset
        fields = self._get_select(queryset.query.distinct)
        queryset = tree.add_select(queryset=queryset,
                                   include_pk=include_pk,
                                   *fields)

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
        ordering = self.ordering
        if ordering:
            ids = zip(*ordering)[0]
        return self._get_concepts(ids)

    def get_fields_for_order_by(self):
        ids = []
        ordering = self.ordering
        if ordering:
            ids = zip(*ordering)[0]
        return self._get_fields_for_concepts(ids)


def convert_legacy(attrs):
    facets = []
    columns = attrs.get('columns', [])
    ordering = attrs.get('ordering', [])

    # Map to position
    _ordering = {}

    for i, (concept, direction) in enumerate(ordering):
        _ordering[concept] = i

    for pk in columns:
        facet = {
            'concept': pk,
            'sort': None,
            'sort_index': None,
            'visible': True,
        }

        if pk in _ordering:
            index = _ordering.pop(pk)
            facet['sort'] = ordering[index][1]
            facet['sort_index'] = index

        facets.append(facet)

    # Append the sort only concepts
    for pk in _ordering:
        index = _ordering[pk]

        facets.append({
            'visible': False,
            'concept': pk,
            'sort': ordering[index][1],
            'sort_index': index,
        })

    return facets


def validate(facets, **context):
    if not facets:
        return None

    from avocado.models import DataConcept

    # Legacy format
    if isinstance(facets, dict):
        warn('The dict-based view structure has been deprecated. '
             'A list of facets objects must now be provided.',
             DeprecationWarning)
        facets = convert_legacy(facets)

    for attrs in facets:
        enabled = attrs.pop('enabled', None)
        attrs.pop('errors', None)
        attrs.pop('warnings', None)
        errors = []
        warnings = []

        concept = None

        if 'concept' not in attrs:
            enabled = False
            errors.append('Concept is required')
        else:
            try:
                concept = DataConcept.objects.get(pk=attrs.get('concept'))
            except DataConcept.DoesNotExist:
                enabled = False
                errors.append('Concept does not exist')

        if attrs.get('sort') and attrs['sort'] not in SORT_DIRECTIONS:
            warnings.append('Invalid sort direction. Must be "asc" or "desc"')

        if concept and not concept.sortable:
            warnings.append('Cannot sort by concept')

        if enabled is False:
            attrs['enabled'] = False

        # Amend errors and warnings if present
        if errors:
            attrs['errors'] = errors

        if warnings:
            attrs['warnings'] = warnings

    return facets


def parse(facets, **context):
    if not facets:
        return Node(**context)

    # Legacy format
    if isinstance(facets, dict):
        warn('The dict-based view structure has been deprecated. '
             'A list of facets objects must now be provided.',
             DeprecationWarning)
        facets = convert_legacy(facets)

    return Node(facets, **context)
