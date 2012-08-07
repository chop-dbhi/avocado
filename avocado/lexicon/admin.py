from django.contrib.admin import ModelAdmin


class LexiconAdmin(ModelAdmin):
    fields = ['label', 'value', 'code', 'order']
    list_display = ['pk'] + fields
    list_editable = fields
