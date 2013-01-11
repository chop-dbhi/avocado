from django.core.management.base import BaseCommand, CommandError
from .utils import get_fields_by_label


class DataFieldCommand(BaseCommand):
    args = '(app | app.model | app.model.field)*'

    def handle_fields(self, *args, **kwargs):
        raise NotImplemented('Subclasses must define this method.')

    def handle(self, *labels, **kwargs):
        if not labels:
            raise CommandError('At least one label for looking up DataFields must be specified.')

        try:
            fields = get_fields_by_label(labels)
        except Exception, e:
            raise CommandError(e.message)
        return self.handle_fields(fields, **kwargs)
