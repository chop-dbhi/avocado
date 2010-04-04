from django.contrib import admin
from avocado.columns.models import ColumnConceptField, ColumnConcept

def make_public(modeladmin, request, queryset):
    queryset.update(is_public=True)
make_public.short_description = 'Mark selected as public'

def make_not_public(modeladmin, request, queryset):
    queryset.update(is_public=False)
make_not_public.short_description = 'Mark selected as not public'


class ColumnConceptFieldInline(admin.TabularInline):
    model = ColumnConceptField


class ColumnConceptAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_public', 'pretty_formatter', 'raw_formatter',
        'category')
    list_filter = ('is_public', 'category', 'pretty_formatter',
        'raw_formatter')
    search_fields = ('name', 'description', 'keywords')
    inlines = (ColumnConceptFieldInline,)
    actions = (make_public, make_not_public)
    save_as = True

class EditorsColumnConceptAdmin(admin.ModelAdmin):
    "Limited set of fields that won't break anything."
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'description', 'keywords')

    fieldsets = (
        (None, {'fields': ('name', 'description', 'keywords', 'category')}),
    )

admin.site.register(ColumnConcept, ColumnConceptAdmin)
