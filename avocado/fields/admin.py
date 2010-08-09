from django.contrib import admin

from avocado.concepts.admin import ConceptAdmin
from avocado.fields.models import Field
from avocado.fields.forms import FieldAdminForm

class FieldAdmin(ConceptAdmin):
    form = FieldAdminForm


admin.site.register(Field, FieldAdmin)
