from django.core.urlresolvers import reverse
from avocado.models import Criterion

__all__ = ('CriterionProxy', 'CategoryProxy')

class CriterionProxy(Criterion):
    class Meta:
        proxy = True

    def json(self):
        json = {
            'id': self.id,
            'uri': reverse('api:criteria:read', args=(self.id,)),
            'name': self.name,
            'description': self.full_description(),
        }
        return json
