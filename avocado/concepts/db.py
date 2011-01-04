def postgresql_psycopg2(queryset, terms):
    column = '"%s"."search_tsv"' % queryset.model._meta.db_table

    if not terms:
        return queryset

    queryset = queryset.extra(where=(column + ' @@ to_tsquery(%s)',),
        params=('&'.join(terms),))

    return queryset
