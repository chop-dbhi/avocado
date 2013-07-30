import inspect
from django.db import models, transaction
from django.db.models.query import QuerySet
from django.contrib.contenttypes.models import ContentType
from avocado.conf import settings
from .utils import get_object_data


class RevisionManager(models.Manager):
    def get_for_model(self, model):
        """Returns all revisions across instances for a model.

        A model is required or a QuerySet can be supplied instead to restrict
        which object revisions are returned.
        """
        if inspect.isclass(model) and issubclass(model, models.Model):
            kwargs = {
                'content_type': ContentType.objects.get_for_model(model),
            }
        elif isinstance(model, QuerySet):
            queryset = model
            model = queryset.model

            kwargs = {
                'object_id__in': queryset.values_list('pk', flat=True).order_by(),
                'content_type': ContentType.objects.get_for_model(model),
            }
        else:
            raise ValueError('A model class or QuerySet is required')
        return self.filter(**kwargs)

    def get_for_object(self, obj, model=None):
        "Returns all revisions for the object."
        queryset = None

        if model is not None:
            queryset = self.get_for_model(model)

        if isinstance(obj, models.Model):
            if queryset is None:
                queryset = self.get_for_model(obj.__class__)
            return queryset.filter(object_id=obj.pk)

        if queryset is None:
            raise ValueError('A model or queryset must be supplied if a primary key is used')

        return queryset.filter(object_id=pk)

    @transaction.commit_on_success
    def cull_for_object(self, obj, model=None, max_size=None):
        if max_size is None:
            max_size = settings.HISTORY_MAX_SIZE
        revisions = self.get_for_object(obj, model=model)\
            .order_by('timestamp').values_list('pk', flat=True)
        self.filter(pk__in=revisions[max_size:]).delete()

    def latest_for_model(self, model):
        "Returns the latest revision across instances for a model."
        try:
            return self.get_for_model(model).latest()
        except self.model.DoesNotExist:
            pass

    def latest_for_object(self, obj, model=None):
        "Returns the latest revision for the object."
        try:
            return self.get_for_object(obj, model=model).latest()
        except self.model.DoesNotExist:
            pass

    def object_has_changed(self, obj, model=None, fields=None):
        "Returns true if the object data has changed since the last revision."
        revision = self.latest_for_object(obj, model=model)
        if revision is None:
            return True
        return bool(revision.diff(obj, fields=fields))

    def create_revision(self, obj, fields, model=None, commit=True, deleted=False, **kwargs):
        """Creates a revision for the object.

        The previous revision will be compared against to prevent having
        a redundant revision.
        """
        if deleted or self.object_has_changed(obj, model=model, fields=fields):
            data = get_object_data(obj, fields)
            revision = self.model(content_object=obj, data=data,
                deleted=deleted, **kwargs)
            if commit:
                revision.save()
            return revision

    @transaction.commit_on_success
    def revert(self, obj, model=None, commit=True):
        "Revert object to last revision."
        revision = self.get_latest_for_object(obj, model=model)
        if revision:
            revision.apply(obj, commit=commit)
        return obj
