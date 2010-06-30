from django.contrib import admin

from avocado.concepts.admin import ConceptAdmin
from avocado.fields.models import FieldConcept
from avocado.fields.forms import FieldConceptAdminForm

class FieldConceptAdmin(ConceptAdmin):
    form = FieldConceptAdminForm


admin.site.register(FieldConcept, FieldConceptAdmin)