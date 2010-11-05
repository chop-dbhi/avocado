import datetime

from django.utils import simplejson
from django.http import HttpResponse
from django.db.models.query import QuerySet, ValuesQuerySet

class JSONHttpResponse(HttpResponse):
    def __init__(self, content, *args, **kwargs):
        content = content or {}
        super(JSONHttpResponse, self).__init__(simplejson.dumps(content),
            'application/json', *args, **kwargs)


class ExcelResponse(HttpResponse):
    def __init__(self, data, output_name='excel_data', headers=None,
                 has_id=True, force_csv=False, encoding='utf8'):

        valid_data = False

        if headers is None:
            l = len(data[0])
            if has_id:
                l -= 1
            headers = ['' for i in range(l)]
        else:
            if has_id:
                headers = [''] + headers

        # Make sure we've got the right type of data to work with
        if isinstance(data, ValuesQuerySet):
            data = list(data)
        elif isinstance(data, QuerySet):
            data = list(data.values())
        if hasattr(data, '__getitem__'):
            if isinstance(data[0], dict):
                if headers is None:
                    headers = data[0].keys()
                data = [[row[col] for col in headers] for row in data]
                data.insert(0, headers)
            if hasattr(data[0], '__getitem__'):
                valid_data = True
                data = [headers] + list(data)
        assert valid_data is True, "ExcelResponse requires a sequence of sequences"

        import cStringIO as StringIO
        output = StringIO.StringIO()

        # Excel has a limit on number of rows; if we have more than that, make a csv
        use_xls = False
        if len(data) <= 65536 and force_csv is not True:
            try:
                import xlwt
                use_xls = True
            except ImportError:
                pass

        if use_xls:
            book = xlwt.Workbook(encoding=encoding)
            sheet = book.add_sheet('Sheet 1')
            styles = {'datetime': xlwt.easyxf(num_format_str='yyyy-mm-dd hh:mm:ss'),
                      'date': xlwt.easyxf(num_format_str='yyyy-mm-dd'),
                      'time': xlwt.easyxf(num_format_str='hh:mm:ss'),
                      'default': xlwt.Style.default_style}

            for rowx, row in enumerate(data):
                for colx, value in enumerate(row):
                    if colx == 0 and has_id:
                        continue
                    if isinstance(value, datetime.datetime):
                        cell_style = styles['datetime']
                    elif isinstance(value, datetime.date):
                        cell_style = styles['date']
                    elif isinstance(value, datetime.time):
                        cell_style = styles['time']
                    else:
                        cell_style = styles['default']
                    sheet.write(rowx, colx, value, style=cell_style)
            book.save(output)
            mimetype = 'application/vnd.ms-excel'
            file_ext = 'xls'
        else:
            for row in data:
                out_row = []
                for i, value in enumerate(row):
                    if i == 0 and has_id:
                        continue
                    if not isinstance(value, basestring):
                        value = unicode(value)
                    value = value.encode(encoding)
                    out_row.append(value.replace('"', '""'))
                output.write('"%s"\n' %
                             '","'.join(out_row))
            mimetype = 'text/csv'
            file_ext = 'csv'
        output.seek(0)
        super(ExcelResponse, self).__init__(content=output.getvalue(),
                                            mimetype=mimetype)
        self['Content-Disposition'] = 'attachment;filename="%s.%s"' % \
            (output_name.replace('"', '\"'), file_ext)

