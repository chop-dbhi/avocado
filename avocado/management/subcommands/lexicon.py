import re
from django.db.models import get_model
from django.core.management.base import BaseCommand, CommandError
from avocado.models import DataField
from avocado.lexicon.managers import coerce_float

non_alnum = re.compile(r'[^a-zA-Z0-9\-]+')


class Command(BaseCommand):
    """
    SYNOPSIS::

        python manage.py avocado lexicon [options...] field model

    DESCRIPTION:

        Creates a lexicon derived from `field` into the Lexicon
        subclass `model`. The distinct list of values for `field`
        will be queried and loaded into the table.
    """

    help = '\n'.join([
        'Creates a lexicon derived from `field` into the Lexicon',
        'subclass `model`. The distinct list of values for `field`',
        'will be queried and loaded into the table.'
    ])

    args = 'field model'

    def handle(self, field_label, model_label, **options):
        model = get_model(*model_label.split('.'))

        if model is None:
            raise CommandError('Not model named {} was found'.format(model_label))

        toks = field_label.split('.')
        if len(toks) != 3:
            raise CommandError('{} is not a valid field identifier. Use a ' \
                '"." delimited notation, e.g. "app.model.field"'.format(field_label))
        datafield = DataField(app_name=toks[0], model_name=toks[1],
            field_name=toks[2])

        if not datafield.field:
            raise CommandError('The field {} could not be found.'.format(field_label))

        count = 0
        values = list(datafield.values)
        values.sort(key=coerce_float)

        for value in values:
            if value is None or value == '':
                continue
            label = non_alnum.sub(value, ' ').title()
            obj = model(label=label, value=value, order=count, code=count)
            obj.save()
            count += 1

        print('{} distinct values loaded'.format(count))
