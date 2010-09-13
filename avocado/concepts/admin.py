from django.contrib import admin

from avocado.concepts.models import Category

__all__ = ('ConceptAdmin', 'EditorsConceptAdmin')

def make_public(modeladmin, request, queryset):
    queryset.update(is_public=True)
make_public.short_description = 'Mark selected as public'

def make_not_public(modeladmin, request, queryset):
    queryset.update(is_public=False)
make_not_public.short_description = 'Mark selected as not public'

class ConceptAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_public')
    list_filter = ('is_public', 'category')
    list_editable = ('is_public',)
    list_per_page = 25
    ordering = ('-is_public',)

    search_fields = ('name', 'description', 'keywords')

    actions = (make_public, make_not_public)
    save_as = True


class EditorsConceptAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_public')
    list_filter = ('is_public', 'category')
    list_per_page = 25
    ordering = ('-is_public',)

    search_fields = ('name', 'description', 'keywords')

    readonly_fields = ('is_public',)

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'keywords', 'category',
                'is_public')
        }),
    )

admin.site.register(Category)
