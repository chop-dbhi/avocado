"Caching utilities for the `columns' package."

COLUMN_CACHE_KEY = 'avocado:columnconcept:%s'
COLUMN_FIELD_CACHE_KEY = 'avocado:columnconcept:fields:%s'

def get_column_fields(concept):
    """Simple interface for getting (and setting) a concept's fields
    from global cache.
    """
    key = COLUMN_FIELD_CACHE_KEY % concept.id

    fields = cache.get(key, None)
    if fields is None:
        fields = list(concept.fields.order_by('columnconceptfield__order'))
        cache.set(key, fields)
    return fields
