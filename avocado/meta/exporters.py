import csv
from django.http import HttpReponse
from modeltree.query import ModelTreeQuerySet
from avocado.utils import loader

class Exporter(object):
    "The base class for all Exporters."

    preferred_formats = ()

    def __init__(self, queryset, concepts):
        if not isinstance(queryset, ModelTreeQuerySet):
            queryset = queryset._clone(klass=ModelTreeQuerySet)

        self.queryset = queryset
        self.concepts = concepts

    def _get_raw_query(self, concepts):
        fields = []

        for c in concepts:
            fields.extend([d.field for d in c.fields.all()])

        raw_query = self.queryset.select(*fields)

        return raw_query

    def _read_row(self, row, formatters):
        for i, (c, f) in enumerate(formatters):
            data, row = row[:f.length], row[f.length:]
            values = c.get_formatter_values(data)
            yield f(values, c)

    def read(self, concepts=None):
        concepts = concepts or self.concepts

        # cache each concept formatter a head of time
        formatters = [(x, x.get_formatter(self.preferred_formats)) \
            for x in concepts]

        for row in iter(self._get_raw_query(concepts)):
            yield self._read_row(row, formatters)

    def export(self, buff):
        headers = []
        table_gen = self.read()

        csv_writer = csv.writer(buff, quoting=csv.QUOTE_MINIMAL)

        for i, row_gen in enumerate(table_gen):

            row = []
            for data in row_gen:
                values = data.values()
                if i == 0:
                    headers.extend([x['name'] for x in values])

                for value in values:
                    row.append(value)

            csv_writer.writerow(row, )
            # closing of this row..
            # write header if first row
            # write data

        # closing out file...


def export(request):
    # get exporter given requst

    exporter = Exporter()
    resp = HttpReponse()

    gen = exporter.export(resp)

    return resp


# initialize the registry that will contain all classes for this type of
# registry
registry = loader.Registry()

# this will be invoked when it is imported by models.py to use the
# registry choices
loader.autodiscover('exporters')
