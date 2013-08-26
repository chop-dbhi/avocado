from .models import Revision


def post_save_revision(instance, created, **kwargs):
    from . import registry
    fields = registry[instance.__class__]['fields']
    user = getattr(instance, 'user')
    session_key = getattr(instance, 'session_key')
    Revision.objects.create_revision(instance, fields=fields, user=user,
        session_key=session_key)


def pre_delete_revision(instance, **kwargs):
    from . import registry
    fields = registry[instance.__class__]['fields']
    user = getattr(instance, 'user')
    session_key = getattr(instance, 'session_key')
    Revision.objects.create_revision(instance, fields=fields, deleted=True,
        user=user, session_key=session_key)
