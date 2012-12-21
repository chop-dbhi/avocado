from django.db import models
from .managers import LexiconManager


class Lexicon(models.Model):
    """Abstract class for defining a lexicon.

    To implement, subclass and define the `value` and `label` fields.
    Avocado treats Lexicon subclasses specially since it is such a
    common practice to have tables that represent a lexicon.

    A few of the advantages include:

        - define an arbitrary order of the items
        - define a integer `code` which is useful for downstream clients that
        prefer working with a enumerable set of values such as SAS or R
        - define a verbose/more readable label for each item

    Avocado integrates Lexicon subclasses by using them in the following ways:

        - performing an `init` will ignore the `label`, `code`, and `order`
        fields since they are supplementary to the `value`
        - using a DataField that represents a field on a Lexicon subclass will
        use the `order` field whenever accessing values or applying it to
        a query
    """
    code = models.IntegerField(null=True)
    order = models.IntegerField(default=0)

    objects = LexiconManager()

    class Meta(object):
        abstract = True
        ordering = ['order']

    def __unicode__(self):
        return unicode(self.label or self.value)
