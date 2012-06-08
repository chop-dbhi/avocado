from django.contrib import admin
from django.core.urlresolvers import reverse
from avocado.models import DataField, DataConcept, DataCategory, DataConceptField
from avocado.forms import DataFieldAdminForm

class PublishedAdmin(admin.ModelAdmin):
    list_per_page = 25
    save_as = True
    actions_on_bottom = True

    # Filter by status
    list_filter = ('published', 'archived')

    # Archived are at the bottom, followed by unpublished, then by name
    ordering = ('archived', '-published', 'name')

    # List here to enable viewing the data
    readonly_fields = ('created', 'modified')
    # TODO change behavior to use Haystack
    search_fields = ('name', 'description', 'keywords')

    # Actions to toggle published and archived status
    actions = ('mark_published', 'mark_unpublished', 'mark_archived',
        'mark_unarchived')

    # Override to make the description consistent with the rest of
    # the actions
    def get_actions(self, request):
        actions = super(PublishedAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            actions['delete_selected'][0].short_description = 'Delete'
        return actions

    def mark_published(self, request, queryset):
        queryset.update(published=True)
    mark_published.short_description = 'Publish'

    def mark_unpublished(self, request, queryset):
        queryset.update(published=False)
    mark_unpublished.short_description = 'Unpublish'

    def mark_archived(self, request, queryset):
        queryset.update(archived=True)
    mark_archived.short_description = 'Archive'

    def mark_unarchived(self, request, queryset):
        queryset.update(archived=False)
    mark_unarchived.short_description = 'Unarchive'


class DataFieldAdmin(PublishedAdmin):
    form = DataFieldAdminForm

    list_display = ('name', 'published', 'archived', 'orphan_status',
        'model_name', 'enumerable', 'searchable', 'related_dataconcepts')
    list_filter = ('published', 'archived', 'model_name', 'enumerable',
        'searchable')
    list_editable = ('published', 'archived', 'enumerable', 'searchable')

    search_fields = ('name', 'description', 'keywords')
    readonly_fields = ('created', 'modified', 'data_modified')
    actions = ('mark_published', 'mark_unpublished', 'mark_archived',
        'mark_unarchived', 'create_dataconcept')

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'name_plural',
                'description',
                'keywords',
                'unit',
                'unit_plural',
                'published',
                'archived',
            ),
        }),

        ('Query Modifiers', {
            'fields': ('translator', 'enumerable', 'searchable')
        }),

        ('Data Source', {
            'description': ('These fields should not be altered in-place. '
                'If where this field is located has changed, change these '
                ' values and create a new field by using "Save as new".'),
            'classes': ('collapse',),
            'fields': ('app_name', 'model_name', 'field_name', 'data_source'),
        }),

        ('Times of Interest', {
            'fields': ('created', 'modified', 'data_modified'),
        }),
    )

    def orphan_status(self, obj):
        if obj.model is None:
            return 'Unknown Model'
        if obj.field is None:
            return 'Unknown Model Field'
        return 'OK'
    orphan_status.short_description = 'Orphan Status'

    def related_dataconcepts(self, obj):
        queryset = obj.concepts.only('id', 'name')
        reverse_name = 'admin:avocado_dataconcept_change'
        urlize = lambda x: '<a href="{0}">{1}</a>'.format(reverse(reverse_name, args=[x.id]), x.name)
        return '<br>'.join(map(urlize, queryset)) or None
    related_dataconcepts.short_description = 'Related Data Concepts'
    related_dataconcepts.allow_tags = True

    def create_dataconcept(self, request, queryset):
        for datafield in queryset:
            DataConcept.objects.create_from_field(datafield)
    create_dataconcept.short_description = 'Create Data Concept'


class DataConceptFieldInlineAdmin(admin.TabularInline):
    model = DataConceptField


class DataConceptAdmin(PublishedAdmin):
    list_display = ('name', 'published', 'archived', 'category',
        'queryview', 'formatter', 'related_datafields')
    list_editable = ('published', 'archived', 'category', 'queryview',
        'formatter')
    inlines = [DataConceptFieldInlineAdmin]

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'name_plural',
                'description',
                'keywords',
                'category',
                'published',
                'archived',
            ),
        }),

        ('Modifiers', {
            'fields': ('queryview', 'formatter'),
        }),

        ('Times of Interest', {
            'fields': ('created', 'modified'),
        }),
    )

    def related_datafields(self, obj):
        queryset = obj.fields.only('id', 'name')
        reverse_name = 'admin:avocado_datafield_change'
        urlize = lambda x: '<a href="{0}">{1}</a>'.format(reverse(reverse_name, args=[x.id]), x.name)
        return '<br>'.join(map(urlize, queryset)) or None
    related_datafields.short_description = 'Related Data Fields'
    related_datafields.allow_tags = True


admin.site.register(DataField, DataFieldAdmin)
admin.site.register(DataConcept, DataConceptAdmin)
admin.site.register(DataCategory)
