from django.contrib import admin

def make_public(modeladmin, request, queryset):
    queryset.update(is_public=True)
make_public.short_description = 'Mark selected as public'

def make_not_public(modeladmin, request, queryset):
    queryset.update(is_public=False)
make_not_public.short_description = 'Mark selected as not public'

class ConceptAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_public', 'category')
    list_filter = ('is_public', 'category')
    list_editable = ('is_public',)
    list_per_page = 25
    
    search_fields = ('name', 'description', 'keywords')
    
    actions = (make_public, make_not_public)
    save_as = True


class EditorsConceptAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_public', 'category')
    list_filter = ('is_public', 'category',)
    list_per_page = 25
    
    search_fields = ('name', 'description', 'keywords')

    readonly_fields = ('is_public',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'keywords', 'category',
                'is_public')
        }),
    )