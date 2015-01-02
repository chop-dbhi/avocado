def sql_string(queryset):
    "Returns an formatted SQL string."
    sql, params = queryset.query.sql_with_params()
    return sql % tuple([repr(str(x)) for x in params])
