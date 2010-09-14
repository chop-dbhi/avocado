from django.contrib import admin
from django.contrib.auth.models import User, Group, Permission

from avocado.contrib.server.admin import main_admin

class UserAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Groups', {'fields': ('groups',)}),
    )

    class Meta:
        model = User

# unregister default one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

main_admin.register(User, UserAdmin)
main_admin.register(Group)
main_admin.register(Permission)