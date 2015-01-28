from django import forms
from django.db import transaction, models
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from avocado.models import DataField, DataConcept, DataCategory, \
    DataConceptField, DataView, DataContext, DataQuery


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


class DataFieldAdminForm(forms.ModelForm):
    def clean_app_name(self):
        app_name = self.cleaned_data.get('app_name')
        try:
            models.get_app(app_name)
        except ImproperlyConfigured:
            raise forms.ValidationError(u'The app "{0}" could not be found'
                                        .format(app_name))
        return app_name

    def clean(self):
        cleaned_data = self.cleaned_data
        app_name = self.cleaned_data.get('app_name')
        model_name = cleaned_data.get('model_name')
        field_name = cleaned_data.get('field_name')

        model = models.get_model(app_name, model_name)

        if model is None:
            del cleaned_data['model_name']
            msg = u'The model "{0}" could not be found in the app "{1}"' \
                .format(model_name, app_name)
            self._errors['model_name'] = self.error_class([msg])
        elif not model._meta.get_field_by_name(field_name):
            del cleaned_data['field_name']
            msg = u'The model "{0}" does not have a field named "{1}"' \
                .format(model_name, field_name)
            self._errors['field_name'] = self.error_class([msg])

        return cleaned_data

    class Meta(object):
        model = DataField


class DataFieldAdmin(PublishedAdmin):
    form = DataFieldAdminForm

    list_display = ('name', 'published', 'archived', 'type',
                    'orphan_status', 'model_name', 'enumerable', 'indexable',
                    'related_dataconcepts')

    list_filter = ('published', 'archived', 'model_name', 'type',
                   'enumerable', 'indexable')

    list_editable = ('published', 'archived', 'enumerable',
                     'indexable', 'type')

    search_fields = ('name', 'description', 'keywords')

    readonly_fields = ('created', 'modified', 'data_version')

    actions = ('mark_published', 'mark_unpublished', 'mark_archived',
               'mark_unarchived', 'create_dataconcept_multi',
               'create_dataconcept_single')

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

        ('Reference Field', {
            'fields': ('app_name', 'model_name', 'field_name'),
            'description': 'The reference field of this DataField. See the '
                           'available supplementary to alter the behavior in '
                           'API.',
        }),

        ('Supplementary Fields', {
            'fields': ('label_field_name', 'search_field_name',
                       'code_field_name', 'order_field_name'),
            'description': 'Fields that can be defined to alter the behavior '
                           'of the DataField API.',
        }),

        ('Modifiers', {
            'fields': ('translator', 'enumerable', 'indexable', 'type')
        }),

        ('Times of Interest', {
            'fields': ('created', 'modified'),
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
        site = self.admin_site
        queryset = obj.concepts.only('id', 'name')
        reverse_name = '{0}:avocado_dataconcept_change'.format(site.name)

        urlize = lambda x: u'<a href="{0}">{1}</a>'.format(reverse(
            reverse_name, args=[x.id]), x.name, namespace=site.name,
            app_name=site.app_name)

        return '<br>'.join(map(urlize, queryset)) or None

    related_dataconcepts.short_description = 'Related Data Concepts'
    related_dataconcepts.allow_tags = True

    def create_dataconcept_multi(self, request, queryset):
        for datafield in queryset:
            DataConcept.objects.create_from_field(datafield)
    create_dataconcept_multi.short_description = 'Create Data Concept for Each'

    @transaction.commit_on_success
    def create_dataconcept_single(self, request, queryset):
        fields = list(queryset)

        # If only a single field is selected with this action, directly map
        if len(fields) == 1:
            DataConcept.objects.create_from_field(fields[0])
            return

        max_length = DataConcept._meta.get_field_by_name('name')[0].max_length
        name = ', '.join([f.name for f in fields])[:max_length - 5] + '...'
        concept = DataConcept(name=u'"{0}"'.format(name))
        concept.save()
        for i, datafield in enumerate(queryset):
            DataConceptField(concept=concept, field=datafield, order=i).save()
    create_dataconcept_single.short_description = 'Create Data Concept for ' \
        'Selected'


class DataConceptFieldInlineAdmin(admin.TabularInline):
    model = DataConceptField


class DataConceptAdmin(PublishedAdmin):
    list_display = ('name', 'published', 'archived', 'type',
                    'category', 'order', 'formatter', 'viewable',
                    'queryable', 'sortable', 'indexable', 'related_datafields')

    list_editable = ('published', 'archived', 'type', 'category',
                     'order', 'formatter', 'viewable', 'queryable',
                     'sortable', 'indexable')

    list_filter = ('published', 'archived', 'category', 'type',
                   'formatter', 'viewable', 'queryable', 'sortable',
                   'indexable')

    ordering = ('archived', '-published', 'category__parent__order',
                'category__order', 'order', 'name')

    inlines = [DataConceptFieldInlineAdmin]

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'name_plural',
                'description',
                'keywords',
                'category',
                'order',
                'published',
                'archived',
            ),
        }),

        ('Modifiers', {
            'fields': ('formatter', 'viewable', 'queryable', 'indexable',
                       'sortable', 'type'),
        }),

        ('Times of Interest', {
            'fields': ('created', 'modified'),
        }),
    )

    def related_datafields(self, obj):
        site = self.admin_site
        queryset = obj.fields.only('id', 'name')
        reverse_name = '{0}:avocado_datafield_change'.format(site.name)

        urlize = lambda x: u'<a href="{0}">{1}</a>'.format(reverse(
            reverse_name, args=[x.id]), x.name, namespace=site.name,
            app_name=site.app_name)

        return '<br>'.join(map(urlize, queryset)) or None

    related_datafields.short_description = 'Related Data Fields'
    related_datafields.allow_tags = True


class DataCategoryAdmin(admin.ModelAdmin):
    model = DataCategory

    list_display = ('name', 'parent', 'order', 'published')

    list_editable = ('parent', 'order', 'published')

    ordering = ('archived', '-published', 'parent__order', 'order', 'name')


class DataViewAdmin(admin.ModelAdmin):
    readonly_fields = ('session_key',)

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'description',
                'keywords',
            ),
        }),

        ('User', {
            'fields': ('user', 'session_key', 'session')
        }),

        ('Template', {
            'fields': ('template', 'default')
        }),

        ('JSON', {
            'fields': ('json',),
            'description': 'JSON representation of the view',
        }),
    )


class DataContextAdmin(admin.ModelAdmin):
    readonly_fields = ('session_key',)

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'description',
                'keywords',
            ),
        }),

        ('User', {
            'fields': ('user', 'session_key', 'session')
        }),

        ('Template', {
            'fields': ('template', 'default')
        }),

        ('JSON', {
            'fields': ('json',),
            'description': 'JSON representation of the context',
        }),
    )


class DataQueryAdmin(admin.ModelAdmin):
    readonly_fields = ('session_key',)

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'description',
                'keywords',
                'public',
            ),
        }),

        ('User', {
            'fields': ('user', 'session_key', 'session')
        }),

        ('Template', {
            'fields': ('template', 'default')
        }),

        ('JSON', {
            'fields': ('view_json', 'context_json'),
            'description': 'JSON representation of the context and view',
        }),
    )


admin.site.register(DataField, DataFieldAdmin)
admin.site.register(DataConcept, DataConceptAdmin)
admin.site.register(DataCategory, DataCategoryAdmin)

admin.site.register(DataView, DataViewAdmin)
admin.site.register(DataContext, DataContextAdmin)
admin.site.register(DataQuery, DataQueryAdmin)
