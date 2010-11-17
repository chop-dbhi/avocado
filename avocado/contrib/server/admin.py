from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from avocado.models import *
from avocado.admin import *

class MainAdminSite(AdminSite):
    "This acts as the main admin site for superusers."
    def has_permission(self, request):
        return super(MainAdminSite, self).has_permission(request) and \
            request.user.is_superuser


class EditorsAdminSite(AdminSite):
    "The admin site for editors of meta data."
    def has_permission(self, request):
        user = request.user
        has_perm = user.groups.filter(name__iexact='editors').exists()
        return super(EditorsAdminSite, self).has_permission(request) and \
            has_perm or user.is_superuser


main_admin = MainAdminSite()
editors_admin = EditorsAdminSite()

main_admin.register(Category)
main_admin.register(Criterion, CriterionAdmin)
main_admin.register(Column, ColumnAdmin)
main_admin.register(Field, FieldAdmin)
main_admin.register(Report)
main_admin.register(Scope)
main_admin.register(Perspective)

editors_admin.register(Category)
editors_admin.register(Criterion, EditorsConceptAdmin)
editors_admin.register(Column, EditorsConceptAdmin)
editors_admin.register(Field, EditorsFieldAdmin)
