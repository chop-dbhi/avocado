from django.contrib import admin

from avocado.concepts.admin import ConceptAdmin
from avocado.criteria.models import CriterionField, Criterion

__all__ = ('CriterionAdmin',)

class CriterionFieldInline(admin.TabularInline):
    model = CriterionField


class CriterionAdmin(ConceptAdmin):
    inlines = (CriterionFieldInline,)


admin.site.register(Criterion, CriterionAdmin)
