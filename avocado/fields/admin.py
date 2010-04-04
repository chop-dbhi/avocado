from django.contrib import admin
from avocado.fields.models import FieldConcept
#from .forms import FieldAdminForm


#def make_public(modeladmin, request, queryset):
#    queryset.update(is_public=True)
#make_public.short_description = 'Mark selected as public'
#
#def make_not_public(modeladmin, request, queryset):
#    queryset.update(is_public=False)
#make_not_public.short_description = 'Mark selected as not public'
#
#def make_default(modeladmin, request, queryset):
#    queryset.update(is_default=True)
#make_default.short_description = 'Make selected default fields'
#
#def make_not_default(modeladmin, request, queryset):
#    queryset.update(is_default=False)
#make_not_default.short_description = 'Make selected not default fields'
#
#
#class FieldCategoryAdmin(admin.ModelAdmin):
#    list_display = ('display_name', 'name')
#    list_filter = ('is_public',)
#    ordering = ('-is_public', 'display_name')
#    actions = (make_public, make_not_public)
#
#
#class FieldAdmin(admin.ModelAdmin):
#    form = FieldAdminForm
#    list_display = ('display_name', 'model', 'is_public', 'is_default', 'category')
#    list_filter = ('model', 'is_public', 'is_default', 'category', 'datatype')
#    search_fields = ('display_name', 'field_name', 'keywords')
#    ordering = ('-is_public', '-is_default', 'model')
#    save_as = True
#    actions = (make_public, make_not_public, make_default, make_not_default)
#
#    fieldsets = (
#        (None, {
#            'fields': ('model', 'field_name', 'datatype', 'display_name', 'icon',
#                'description', 'keywords', 'category', 'is_public', 'is_default')
#        }),
#        ('Allowed Values', {
#            'fields': ('allowed_values_callback', 'allowed_values_fulltext')
#        }),
#        ('Graphic Info', {
#            'fields': ('graphic_title', 'graphic_xaxis', 'graphic_yaxis', 'graphic_query')
#        })
#    )
#
#
#class EditorsFieldAdmin(admin.ModelAdmin):
#    list_display = ('display_name', 'model', 'is_public', 'is_default', 'category')
#    list_filter = ('model', 'is_public', 'is_default')
#    search_fields = ('display_name', 'field_name', 'keywords')
#    ordering = ('-is_public', '-is_default', 'model')
#
#    fieldsets = (
#        (None, {'fields': ('display_name', 'description', 'keywords', 'category')}),
#    )
#
#
#class EditorsFieldCategoryAdmin(admin.ModelAdmin):
#    list_display = ('display_name', 'name')
#    ordering = ('display_name',)
#
#    fieldsets = (
#        (None, {'fields': ('name', 'display_name')}),
#    )

admin.site.register(FieldConcept)
#admin.site.register(FieldConcept, FieldConceptAdmin)
