from __future__ import print_function
import re
from django.db.models import get_model
from django.core.management.base import BaseCommand, CommandError
from avocado.models import DataField
from avocado.lexicon.managers import coerce_float

non_alnum = re.compile(r'[^a-zA-Z0-9\-]+')

_help = """\
Creates a lexicon derived from `field` into the Lexicon
subclass `model`. The distinct list of values for `field`
will be queried and loaded into the table.
"""


class Command(BaseCommand):
    __doc__ = help = _help

    args = 'field model'

    def handle(self, field_label, model_label, **options):
        model = get_model(*model_label.split('.'))

        if model is None:
            raise CommandError(u'Not model named {0} was found'.format(
                model_label))

        toks = field_label.split('.')
        if len(toks) != 3:
            raise CommandError(u'{0} is not a valid field identifier. Use a '
                               '"." delimited notation, e.g. "app.model.field"'
                               .format(field_label))

        # Not required to be persisted to the database..
        f = DataField(app_name=toks[0], model_name=toks[1], field_name=toks[2])

        if not f.field:
            raise CommandError(u'The field {0} could not be found.'.format(
                field_label))

        count = 0
        values = list(f.values())
        values.sort(key=coerce_float)

        for value in values:
            if value is None or value == '':
                continue
            label = non_alnum.sub(value, ' ').title()
            obj = model(label=label, value=value, order=count, code=count)
            obj.save()
            count += 1

        print(u'{0} distinct values loaded'.format(count))
