from django.db import models, transaction
from django.contrib.contenttypes.models import ContentType
from .utils import get_object_data


class RevisionManager(models.Manager):
    def get_for_object(self, obj):
        "Returns all revisions for the object."
        ctype = ContentType.objects.get_for_model(obj)
        return self.filter(content_type=ctype, object_id=obj.pk)

    def latest_for_object(self, obj):
        "Returns the latest revision for the object."
        ctype = ContentType.objects.get_for_model(obj)
        try:
            return self.filter(content_type=ctype, object_id=obj.pk).latest()
        except self.model.DoesNotExist:
            pass

    def object_has_changed(self, obj, fields=None):
        "Returns true if the object data has changed since the last revision."
        revision = self.latest_for_object(obj)
        if revision is None:
            return True
        return bool(revision.diff(obj, fields=fields))

    def create_revision(self, obj, fields, commit=True, deleted=False, **kwargs):
        """Creates a revision for the object.

        The previous revision will be compared against to prevent having
        a redundant revision.
        """
        if deleted or self.object_has_changed(obj, fields=fields):
            data = get_object_data(obj, fields)
            revision = self.model(content_object=obj, data=data,
                deleted=deleted, **kwargs)
            if commit:
                revision.save()
            return revision

    @transaction.commit_on_success
    def revert(self, obj, commit=True):
        "Revert object to last revision."
        revision = self.get_latest_for_object(obj)
        if revision:
            revision.apply(obj, commit=commit)
        return obj
