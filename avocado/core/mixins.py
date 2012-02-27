from django.db import models
from django.utils.importlib import import_module
from avocado.conf import settings

def import_mixin(app_label):
    if app_label in settings.MIXINS:
        path = settings.MIXINS[app_label].split('.')
        mixin_name = path.pop(-1)
        module = import_module('.'.join(path))
        Mixin = getattr(module, mixin_name)
    else:
        Mixin = models.Model

    return Mixin

def create_mixin(name, module, bases=None, attrs=None, meta=None):
    "Creates an abstract model class based on the provided information."
    bases = bases or (models.Model,)
    attrs = attrs or {}
    meta = meta or {}

    meta.setdefault('abstract', True)

    class Meta(object):
        pass

    # Update Meta with any options that were provided
    if meta:
        for key, value in meta.iteritems():
            setattr(Meta, key, value)

    # Create the initial set of model attributes by copying the fields
    attrs = attrs.copy()
    # Set up a dictionary to simulate declarations within a class
    attrs.update({'__module__': module, 'Meta': Meta})

    # create the class, which automatically triggers ModelBase processing
    return type(name, bases, attrs)

def create_model(name, module, bases=None, fields=None, options=None):
    "Creates a non-abstract model class based on the provided information."
    options = options or {}
    options['abstract'] = False

    return create_mixin(name, module, bases=bases, fields=fields,
        options=options)
