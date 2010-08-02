def add_columns(queryset, columns, modeltree):
    """Takes a `queryset' and ensures the proper table join have been
    setup to display the table columns.
    """
    # TODO determine if the aliases can contain more than one reference
    # to a table

    # add queryset model's pk field
    aliases = [(queryset.model._meta.db_table,
        queryset.model._meta.pk.column)]

    for column in columns:
        queryset, c_aliases = column.add_fields_to_queryset(queryset, modeltree)
        aliases.extend(c_aliases)

    queryset.query.select = aliases
    return queryset

def add_ordering(queryset, column_orders, modeltree):
    """Applies column ordering to a queryset. Resolves a Column's
    fields and generates the `order_by' paths.
    """
    queryset.query.clear_ordering()
    orders = []

    for column, direction in column_orders:
        c_orders = column.get_ordering_for_queryset(modeltree, direction)
        orders.extend(c_orders)

    return queryset.order_by(*orders)
