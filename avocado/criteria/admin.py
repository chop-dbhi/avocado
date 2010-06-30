from django.contrib import admin

from avocado.concepts.admin import ConceptAdmin
from avocado.criteria.models import CriterionConceptField, CriterionConcept

class CriterionConceptFieldInline(admin.TabularInline):
    model = CriterionConceptField


class CriterionConceptAdmin(ConceptAdmin):
    list_display = ('name', 'is_public', 'category')
    inlines = (CriterionConceptFieldInline,)


admin.site.register(CriterionConcept, CriterionConceptAdmin)
