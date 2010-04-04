from django.contrib import admin
from avocado.criteria.models import CriterionConceptField, CriterionConcept

def make_public(modeladmin, request, queryset):
    queryset.update(is_public=True)
make_public.short_description = 'Mark selected as public'

def make_not_public(modeladmin, request, queryset):
    queryset.update(is_public=False)
make_not_public.short_description = 'Mark selected as not public'


class CriterionConceptFieldInline(admin.TabularInline):
    model = CriterionConceptField


class CriterionConceptAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_public', 'category', 'filter_name',
        'view_name', 'template_name')
    list_filter = ('is_public', 'category', 'filter_name')
    search_fields = ('name', 'description', 'keywords')
    inlines = (CriterionConceptFieldInline,)
    actions = (make_public, make_not_public)
    save_as = True

class EditorsCriterionConceptAdmin(admin.ModelAdmin):
    "Limited set of fields that won't break anything."
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'description', 'keywords')

    fieldsets = (
        (None, {'fields': ('name', 'description', 'keywords', 'category')}),
    )


admin.site.register(CriterionConcept, CriterionConceptAdmin)
