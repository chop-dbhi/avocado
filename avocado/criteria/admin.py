from django.contrib import admin

from avocado.concepts.admin import ConceptAdmin
from avocado.criteria.models import CriterionField, Criterion

class CriterionFieldInline(admin.TabularInline):
    model = CriterionField


class CriterionAdmin(ConceptAdmin):
    list_display = ('name', 'is_public', 'category')
    inlines = (CriterionFieldInline,)


admin.site.register(Criterion, CriterionAdmin)
