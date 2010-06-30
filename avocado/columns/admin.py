from django.contrib import admin

from avocado.concepts.admin import ConceptAdmin
from avocado.columns.models import ColumnConcept, ColumnConceptField

class ColumnConceptFieldInline(admin.TabularInline):
    model = ColumnConceptField


class ColumnConceptAdmin(ConceptAdmin):
    inlines = (ColumnConceptFieldInline,)


admin.site.register(ColumnConcept, ColumnConceptAdmin)