from django.contrib import admin
from django.db import transaction
from django.core.urlresolvers import reverse

from avocado.concepts.admin import ConceptAdmin, EditorsConceptAdmin
from avocado.models import Field, Column, Criterion
from avocado.fields.forms import FieldAdminForm

__all__ = ('FieldAdmin', 'EditorsFieldAdmin')


class FieldAdmin(ConceptAdmin):
    form = FieldAdminForm

    list_display = ('name', 'is_public', 'show_orphan_reason', 'model_name',
        'enable_choices', 'criterion_relations', 'column_relations')
    list_filter = ('is_public', 'model_name', 'sites')
    list_editable = ('is_public', 'enable_choices')

    actions = ('create_criterion', 'create_column')

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'keywords', 'is_public'),
        }),

        ('Query Representation', {
            'classes': ('collapse',),
            'fields': ('translator', 'enable_choices')
        }),

        ('Permissions', {
            'classes': ('collapse',),
            'fields': ('group', 'sites')
        }),

        ('Metadata', {
            'description': ('These fields should not be altered in-place. '
                'If where this field is located has changed, change these '
                ' values and create a new field by using "Save as new".'),
            'classes': ('collapse',),
            'fields': ('app_name', 'model_name', 'field_name'),
        }),
    )

    def show_orphan_reason(self, obj):
        if obj.model is None:
            return 'Unknown Model'
        if obj.field is None:
            return 'Unknown Field'
        return 'OK'
    show_orphan_reason.short_description = 'Orphan Status'

    def criterion_relations(self, obj):
        queryset = obj.criterion_set.only('id', 'name')
        urlize = lambda x: '<a href="%s">%s</a>' % (
            reverse('admin:avocado_criterion_change', args=(x.id,)),
            x.name
        )
        return '<br>'.join(map(urlize, queryset)) or None
    criterion_relations.short_description = 'Criterion Relations'
    criterion_relations.allow_tags = True

    def column_relations(self, obj):
        queryset = obj.column_set.only('id', 'name')
        urlize = lambda x: '<a href="%s">%s</a>' % (
            reverse('admin:avocado_column_change', args=(x.id,)),
            x.name
        )
        return '<br>'.join(map(urlize, queryset)) or None
    column_relations.short_description = 'Column Relations'
    column_relations.allow_tags = True

    @transaction.commit_on_success
    def _create_concept(self, model, request, queryset):
        for f in queryset:
            concept = model(name=f.name, is_public=False)
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
