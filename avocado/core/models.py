import logging
from django.db import models
from .managers import PublishedManager

log = logging.getLogger(__file__)


class Base(models.Model):
    """Base abstract class containing general metadata.

        `name` - The name _should_ be unique in practice, but is not enforced
        since in certain cases the name differs relative to the model and/or
        concepts these fields are asssociated with.

        `description` - Will tend to be exposed in client applications since
        it provides context to the end-users.

        `keywords` - Additional extraneous text that cannot be derived from
        the name, description or data itself. This is solely used for search
        indexing.
    """
    # Descriptor-based fields
    name = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    keywords = models.CharField(max_length=100, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta(object):
        abstract = True

    def __unicode__(self):
        return self.name

    def __bytes__(self):
        return self.__unicode__().encode('utf8')

    @property
    def descriptors(self):
        """Returns a dict of fields that represent this model's descriptors.
        This is used for performing text indexing for model instances.
        """
        return {
            'name': unicode(self),
            'description': self.description,
            'keywords': self.keywords,
        }


class BasePlural(Base):
    """Adds field for specifying the plural form of the name.

        `name_plural` - Same as `name`, but the plural form. If not
        provided, an 's' will appended to the end of the `name`.
    """
    name_plural = models.CharField(max_length=200, null=True, blank=True)

    class Meta(object):
        abstract = True

    @property
    def descriptors(self):
        return {
            'name': unicode(self),
            'name_plural': self.get_plural_name(),
            'description': self.description,
            'keywords': self.keywords,
        }

    def get_plural_name(self):
        if self.name_plural:
            return self.name_plural

        name = unicode(self)

        if not name.endswith('s'):
            return name + 's'

        return name


class PublishArchiveMixin(models.Model):
    """Mixin containing the `published` and `archived` fields.

    These fields are used in conjunction with the custom manager that is
    defined for this model. The manager exposes a `published` method that
    returns a queryset of objecs that are published and not archived.

    If an object is saved that is published _and_ archived, the published
    flag will be set to False.
    """
    published = models.BooleanField(default=False)

    archived = models.BooleanField(default=False, help_text=u'Note: archived '
                                   'takes precedence over being published')

    objects = PublishedManager()

    class Meta(object):
        abstract = True

    def save(self, *args, **kwargs):
        if self.archived and self.published:
            self.published = False
            log.debug(u'{0} is published, but is being archived. It has '
                      'been unpublished'.format(self))
        super(PublishArchiveMixin, self).save(*args, **kwargs)
