from django.contrib import admin

from avocado.concepts.models import Category

__all__ = ('ConceptAdmin', 'EditorsConceptAdmin')

class ConceptAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_public', 'order', 'field_relations')
    list_filter = ('is_public', 'category')
    list_editable = ('category', 'is_public', 'order')
    search_fields = ('name', 'description', 'keywords')
    ordering = ('name',)
    list_per_page = 25
    save_as = True


class EditorsConceptAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_public')
    list_filter = ('is_public', 'category')
    search_fields = ('name', 'description', 'keywords')
    ordering = ('name',)
    list_per_page = 25

    readonly_fields = ('is_public',)

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'keywords', 'category',
                'is_public')
        }),
    )


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'order')
    list_editable = ('parent', 'order')


admin.site.register(Category, CategoryAdmin)
