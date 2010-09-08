from django.contrib import admin

from avocado.contrib.server.plugins.store.models import PatientSet

class PatientSetAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'cnt')

admin.site.register(PatientSet)