from datetime import datetime
from django.db import models

class SearchInterface(models.Model):
    # search optimizations
    search_doc = models.TextField(editable=False, null=True)


class ReviewInterface(models.Model):
    """Provides an interface for setting a review status and note for
    representing various stages of integration for an Ontology or
    Field.
    """
    REVIEW_CHOICES = (
        (u'Unreviewed', u'Unreviewed'),
        (u'Embargoed', u'Embargoed'),
        (u'Deprecated', u'Deprecated'),
        (u'Waiting', u'Waiting'),
        (u'Curation Required', u'Curation Required'),
        (u'Curation Pending', u'Curation Pending'),
        (u'Integration Required', u'Integration Required'),
        (u'Integration Pending', u'Integration Pending'),
        (u'Finalized', u'Finalized'),
    )

    status = models.CharField(u'Review status', max_length=40,
        choices=REVIEW_CHOICES, default=REVIEW_CHOICES[0][0])
    note = models.TextField(u'Review note', null=True)
    reviewed = models.DateTimeField(u'Last reviewed')

    def save(self):
        self.reviewed = datetime.now()
        super(ReviewInterface, self).save()


class QueryViewInterface(models.Model):
    view = models.CharField(max_length=100, null=True)
