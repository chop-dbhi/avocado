import logging
from django.db import models
from .managers import PublishedManager

log = logging.getLogger(__file__)


class Base(models.Model):
    """Base abstract class containing general metadata.

        ``name`` - The name _should_ be unique in practice, but is not enforced
        since in certain cases the name differs relative to the model and/or
        concepts these fields are asssociated with.

        ``description`` - Will tend to be exposed in client applications since
        it provides context to the end-users.

        ``keywords`` - Additional extraneous text that cannot be derived from
        the name, description or data itself. This is solely used for search
        indexing.
    """
    # Descriptor-based fields
    name = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    keywords = models.CharField(max_length=100, null=True, blank=True)

    # Availability control mechanisms
    # Rather than deleting objects, they can be archived
    archived = models.BooleanField(default=False,
        help_text=u'Note: archived takes precedence over being published')
    # When `published` is false, it is globally not accessible.
    published = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = PublishedManager()

    class Meta(object):
        abstract = True

    def __unicode__(self):
        return unicode(self.name)

    @property
    def descriptors(self):
        return {
            'name': self.name,
            'description': self.description,
            'keywords': self.keywords,
        }

    def save(self, *args, **kwargs):
        if self.archived and self.published:
            self.published = False
            log.debug('{0} is published, but is being archived. It has ' \
                'been unpublished'.format(self))
        super(Base, self).save(*args, **kwargs)


class BasePlural(Base):
    """Adds field for specifying the plural form of the name.

        ``name_plural`` - Same as ``name``, but the plural form. If not
        provided, an 's' will appended to the end of the ``name``.
    """
    name_plural = models.CharField(max_length=60, null=True, blank=True)

    class Meta(object):
        abstract = True

    @property
    def descriptors(self):
        return {
            'name': self.name,
            'name_plural': self.name_plural,
            'description': self.description,
            'keywords': self.keywords,
        }

    def get_plural_name(self):
        if self.name_plural:
            plural = self.name_plural
        elif self.name and not self.name.endswith('s'):
            plural = self.name + 's'
        else:
            plural = self.name
        return plural
