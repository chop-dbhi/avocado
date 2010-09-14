from django.contrib import admin

from avocado.concepts.admin import ConceptAdmin
from avocado.columns.models import Column, ColumnField

__all__ = ('ColumnAdmin',)

class ColumnFieldInline(admin.TabularInline):
    model = ColumnField


class ColumnAdmin(ConceptAdmin):
    inlines = (ColumnFieldInline,)


admin.site.register(Column, ColumnAdmin)
