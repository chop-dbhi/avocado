from avocado.interfaces import get_base_interface
from .models import ObjectSet


class ObjectSetInterface(get_base_interface()):
    @classmethod
    def valid_for_field(self, field):
        if issubclass(field.model, ObjectSet):
            return True

    @property
    def _label_field(self):
        return self.model._meta.get_field_by_name('name')[0]

    @property
    def _search_field(self):
        return self._label_field

    @property
    def field(self):
        "ObjectSets are optimized for using keys."
        return self.model._meta.pk
