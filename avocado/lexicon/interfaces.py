from django.db import models
from avocado.interfaces import FieldInterface
from .models import Lexicon


class LexiconInterface(FieldInterface):
    supports_coded_values = True

    @classmethod
    def valid_for_field(self, field):
        # Field on the lexicon
        if issubclass(field.model, Lexicon):
            return True
        # Foreign key to lexicon
        if isinstance(field, models.ForeignKey) and issubclass(field.rel.to, Lexicon):
            return True

    def __init__(self, instance, *args, **kwargs):
        super(LexiconInterface, self).__init__(instance, *args, **kwargs)
        self._related = isinstance(instance.field, models.ForeignKey)
        if self._related:
            self._limit_choices_to = instance.field.rel.limit_choices_to

    def _base_queryset(self, **context):
        "Overridden to account for the `limit_choices_to` property."
        queryset = super(LexiconInterface, self)._base_queryset(**context)
        if self._related:
            queryset = queryset.complex_filter(self._limit_choices_to)
        return queryset

    @property
    def _label_field(self):
        return self.model._meta.get_field_by_name('label')[0]

    @property
    def _code_field(self):
        return self.model._meta.get_field_by_name('code')[0]

    @property
    def _order_field(self):
        return self.model._meta.get_field_by_name('order')[0]

    @property
    def model(self):
        if self._related:
            return self._instance.field.rel.to
        return self._instance.model

    @property
    def field(self):
        return self.model._meta.pk
