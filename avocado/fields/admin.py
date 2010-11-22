from django.contrib import admin
from django.db import transaction

from avocado.concepts.admin import ConceptAdmin, EditorsConceptAdmin
from avocado.models import Field, Column, Criterion
from avocado.fields.forms import FieldAdminForm

__all__ = ('FieldAdmin', 'EditorsFieldAdmin')

class FieldAdmin(ConceptAdmin):
    form = FieldAdminForm
    list_display = ('name', 'is_public', 'model_name', 'enable_choices')
    list_filter = ('is_public', 'model_name')
    list_editable = ('is_public', 'enable_choices')

    actions = ('create_criterion', 'create_column')

    @transaction.commit_on_success
    def _create_concept(self, model, request, queryset):
        for f in queryset:
            concept = model(name=f.name, description=f.description,
                keywords=f.keywords, is_public=False)
            concept.save()

            conceptfield = concept.conceptfields.model(field=f,
                concept=concept)
            conceptfield.save()

    def create_criterion(self, request, queryset):
        return self._create_concept(Criterion, request, queryset)
    create_criterion.short_description = 'Create criterion from field'

    def create_column(self, request, queryset):
        return self._create_concept(Column, request, queryset)
    create_column.short_description = 'Create column from field'


class EditorsFieldAdmin(EditorsConceptAdmin):
    list_display = ('name', 'is_public')
    list_filter = ('is_public',)

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'keywords', 'is_public')
        }),
    )


admin.site.register(Field, FieldAdmin)
