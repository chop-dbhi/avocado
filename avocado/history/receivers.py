from .models import Revision


def post_save_revision(instance, created, **kwargs):
    from . import registry
    fields = registry[instance.__class__]['fields']
    Revision.objects.create_revision(instance, fields=fields)


def pre_delete_revision(instance, **kwargs):
    from . import registry
    fields = registry[instance.__class__]['fields']
    Revision.objects.create_revision(instance, fields=fields, deleted=True)
