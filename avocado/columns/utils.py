from avocado.columns.models import Column
from avocado.columns.cache import cache
from avocado.modeltree import DEFAULT_MODELTREE_ALIAS

def column_format_rules(columns, format_type):
    rules = []
    for column in columns:
        if not isinstance(column, Column):
            column = cache.get(column)
        rules.append(column.rule(format_type))
    return rules

def add_columns(queryset, columns, using=DEFAULT_MODELTREE_ALIAS):
    """Takes a ``queryset`` and ensures the proper table join have been
    setup to display the table columns.
    """
    # add queryset model's pk field
    aliases = [(queryset.model._meta.db_table,
        queryset.model._meta.pk.column)]

    for column in columns:
        if not isinstance(column, Column):
            column = cache.get(column)
        queryset, _aliases = column.add_fields_to_queryset(queryset, using)
        aliases.extend(_aliases)

    queryset.query.select = aliases
    return queryset

def add_ordering(queryset, order_rules, using=DEFAULT_MODELTREE_ALIAS):
    """Applies column ordering to a queryset. Resolves a Column's
    fields and generates the `order_by' paths.
    """
    # this will ensure the default ordering is not stripped (specified on the
    # model's Meta class)
    if not order_rules:
        return queryset

    queryset.query.clear_ordering()
    orders = []

    for column, direction in order_rules:
        if not isinstance(column, Column):
            column = cache.get(column)
        _orders = column.get_ordering_for_queryset(direction, using=using)
        orders.extend(_orders)

    return queryset.order_by(*orders)
