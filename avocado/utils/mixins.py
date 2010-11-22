from django.db import models

def create_mixin(name, module, bases=None, fields=None, options=None):
    bases = bases or (models.Model,)

    class Meta(object):
        abstract = True

    # Update Meta with any options that were provided
    if options is not None:
        for key, value in options.iteritems():
            setattr(Meta, key, value)

    # Set up a dictionary to simulate declarations within a class
    attrs = {'__module__': module, 'Meta': Meta}

    # Add in any fields that were provided
    if fields:
        attrs.update(fields)

    # Create the class, which automatically triggers ModelBase processing
    model = type(name, bases, attrs)

    return model
