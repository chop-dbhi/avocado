from django.contrib import admin
from avocado.fields.models import FieldConcept
from avocado.fields.forms import FieldConceptAdminForm

def make_public(modeladmin, request, queryset):
    queryset.update(is_public=True)
make_public.short_description = 'Mark selected as public'

def make_not_public(modeladmin, request, queryset):
    queryset.update(is_public=False)
make_not_public.short_description = 'Mark selected as not public'


class FieldConceptAdmin(admin.ModelAdmin):
    form = FieldConceptAdminForm
    list_display = ('name', 'is_public', 'category')
    list_filter = ('is_public', 'category')
    search_fields = ('name', 'description', 'keywords')
    actions = (make_public, make_not_public)
    save_as = True


admin.site.register(FieldConcept, FieldConceptAdmin)