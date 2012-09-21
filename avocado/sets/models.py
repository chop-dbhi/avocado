import django
from django.db import models, transaction, IntegrityError


class ObjectSetError(Exception):
    def __init__(self, msg=None):
        if msg is None:
            msg = 'ObjectSet instance needs to have a primary key ' \
                'before set operations can be used.'
        Exception.__init__(self, msg)


class ObjectSet(models.Model):
    """Enables persisting a materialized set of IDs for some object type.
    `ObjectSet` must be subclassed to add the many-to-many relationship
    to the _object_ of interest.
    """
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    # In cases where an object set has been created as a result of a
    # data context, a reference can be stored for performing updates
    # as more data is added.
    context = models.OneToOneField('avocado.DataContext', null=True,
        blank=True, editable=False)

    # Stored count of the set size. Since most operations are incremental
    # and are applied with objects in memory, this is a more efficient
    # way to keep track of the count as suppose to performing a database
    # count each time.
    count = models.PositiveIntegerField(default=0, editable=False)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    # Name of field which contains the set of objects
    set_object_rel = None

    class Meta(object):
        abstract = True

    @property
    def _set_object_class(self):
        return getattr(self.__class__, self.set_object_rel).through

    @property
    def _object_field(self):
        opts = self._set_object_class._meta
        return opts.get_field_by_name('set_object')[0]

    @property
    def _object_class(self):
        return self._object_field.rel.to

    @property
    def _all_set_objects(self):
        "Returns a SetObject queryset containing all objects in this set."
        return self._set_object_class.objects.filter(object_set=self)

    @property
    def _set_objects(self):
        "Returns a SetObject queryset containing all non-removed objects."
        return self._all_set_objects.filter(removed=False)

    def __unicode__(self):
        return unicode(self.name)

    def __len__(self):
        "Returns the length (size) of this set."
        return self.count

    def __nonzero__(self):
        return True

    def __iter__(self):
        objects = self._object_class.objects.all()
        pks = self._set_objects.values_list('set_object__pk')
        return iter(objects.filter(pk__in=pks))

    def __contains__(self, obj):
        "Returns True if `obj` is in this set."
        return self._set_objects.filter(set_object=obj).exists()

    def __and__(self, other):
        "Performs an intersection of this set and `other`."
        raise NotImplemented

    def __or__(self, other):
        "Performs an union of this set and `other`."
        raise NotImplemented

    def __xor__(self, other):
        "Performs an exclusive union of this set and `other`."
        raise NotImplemented

    def __sub__(self, other):
        "Removes objects from this set that are in `other`."
        raise NotImplemented

    def __iand__(self, other):
        "Performs an inplace intersection of this set and `other`."
        raise NotImplemented

    def __ior__(self, other):
        "Performs and inplace union of this set and `other`."
        raise NotImplemented

    def __ixor__(self, other):
        "Performs an inplace exclusive union of this set and `other`."
        raise NotImplemented

    def __isub__(self, other):
        "Inplace removal of objects from this set that are in `other`."
        raise NotImplemented

    def _check_pk(self):
        if not self.pk:
            raise ObjectSetError

    def _check_type(self, obj):
        if not isinstance(obj, self._object_class):
            raise TypeError("Only objects of type '{0}' can be added to the "\
                "set".format(self._object_class.__name__))

    def _add(self, obj, added):
        """Check for an existing object that has been removed and mark
        it has not removed, otherwise create a new object and mark it
        as added.
        """
        self._check_type(obj)
        try:
            _obj = self._all_set_objects.get(set_object=obj)
            # Already exists, nothing to do
            if _obj.removed is False:
                return False
            _obj.removed = False
            _obj.added = added
        except self._set_object_class.DoesNotExist:
            _obj = self._set_object_class(set_object=obj, object_set=self,
                added=added)
        _obj.save()
        return True

    @transaction.commit_on_success
    def bulk(self, objs, added=False):
        """Attempts to bulk load objects. Although this is the most efficient
        way to add objects, if any fail to be added, none will be added.

        This should be used when the set is empty and needs to be populated.
        """
        if django.VERSION < (1, 4):
            raise EnvironmentError('This method requires Django 1.4 or above')

        self._check_pk()
        _objs = []
        loaded = 0
        for obj in iter(objs):
            self._check_type(obj)
            _objs.append(self._set_object_class(object_set=self,
                set_object=obj, added=added))
            loaded += 1
        self._set_object_class.objects.bulk_create(_objs)
        self.count += loaded
        self.save()
        return loaded

    @transaction.commit_on_success
    def add(self, obj, added=False):
        "Adds `obj` to the set."
        self._check_pk()
        added = self._add(obj, added)
        if added:
            self.count += 1
            self.save()
        return added

    @transaction.commit_on_success
    def remove(self, obj):
        "Removes `obj` from the set."
        self._check_pk()
        self._check_type(obj)
        removed = self._set_objects.filter(set_object=obj,
            object_set=self).update(removed=True)
        if removed:
            self.count -= 1
            self.save()
        return bool(removed)

    @transaction.commit_on_success
    def update(self, objs, added=True):
        "Update the current set with the objects not already in the set."
        self._check_pk()
        added = 0
        for obj in iter(objs):
            added += int(self._add(obj, added))
        self.count += added
        self.save()
        return added

    @transaction.commit_on_success
    def clear(self):
        "Remove all objects from the set."
        self._check_pk()
        removed = self._set_objects.update(removed=True)
        self.count = 0
        self.save()
        return removed

    @transaction.commit_on_success
    def replace(self, objs):
        "Replace the current set with the new objects."
        self._check_pk()
        self._set_objects.update(removed=True)
        self.count = 0
        return self.update(objs)

    def flush(self):
        "Deletes objects in the set marked as `removed`."
        self._check_pk()
        return self._all_set_objects.filter(removed=True).delete()


class SetObject(models.Model):
    """Adds additional information about the objects that have been `added`
    and `removed` from the original set.

    For instance, additional objects that are added which do not match the
    conditions currently associated with the `ObjectSet` should be flagged
    as `added`. If in the future they match the conditions, the flag can be
    removed.

    Any objects that are removed from the set should be marked as `removed`
    even if they were added at one time. This is too keep track of the objects
    that have been explicitly removed from the set.

    To implement, the `set_object` and `object_set` fields must be defined:

    class BookSetObject(ObjectSet):
        object_set = models.ForeignKey(BookSet)
        set_object = models.ForeignKey(Book)

    """
    added = models.BooleanField(default=False)
    removed = models.BooleanField(default=False)

    class Meta(object):
        abstract = True
        unique_together = ('object_set', 'set_object')
