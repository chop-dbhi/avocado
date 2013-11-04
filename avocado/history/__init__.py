from django.db.models.signals import pre_delete, post_save
from avocado.core.loader import AlreadyRegistered, NotRegistered
from .receivers import pre_delete_revision, post_save_revision
from . import utils


registry = {}


def register(model, fields=None, exclude=None):
    """Registers a model with the specified fields to be automatically
    versioned on save and delete operations.
    """
    if model in registry:
        raise AlreadyRegistered(u'The model {0} is already registered'.format(
            model.__name__))

    if not fields:
        fields = utils.get_model_fields(model)
    if not exclude:
        exclude = ()

    utils.validate_fields(model, fields, exclude)
    fields = tuple(set(fields) - set(exclude))

    if not fields:
        raise ValueError(u'No fields defined for versioning.')

    dispatch_uid = '{0}_revision'.format(model.__name__)

    pre_delete.connect(pre_delete_revision, weak=False, sender=model,
                       dispatch_uid=dispatch_uid)
    post_save.connect(post_save_revision, weak=False, sender=model,
                      dispatch_uid=dispatch_uid)

    registry[model] = {
        'fields': fields,
        'dispatch_uid': dispatch_uid,
    }


def unregister(model):
    "Unregisters a model from versioning."
    if model not in registry:
        raise NotRegistered(u'The model {0} is not registered'.format(
            model.__name__))
    cache = registry.pop(model)
    pre_delete.disconnect(sender=model, dispatch_uid=cache['dispatch_uid'])
    post_save.disconnect(sender=model, dispatch_uid=cache['dispatch_uid'])
