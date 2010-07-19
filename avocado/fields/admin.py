from django.contrib import admin

from avocado.concepts.admin import ConceptAdmin
from avocado.fields.models import ModelField
from avocado.fields.forms import ModelFieldAdminForm

class ModelFieldAdmin(ConceptAdmin):
    form = ModelFieldAdminForm


admin.site.register(ModelField, ModelFieldAdmin)