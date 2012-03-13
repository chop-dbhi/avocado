from django.db.models import ObjectDoesNotExist

def objectset_scope_sync_pre_save(instance, **kwargs):
    """Pre-save handler for both the ``Scope`` object and the ``ObjectSet``
    object. If registered with ``Scope`` as the sender, two additional keyword
    arguments must be partially applied prior to connecting the handler.

    ``set_name`` - the reverse name of the ``ObjectSet`` subclass' instance

    ``set_manager`` - the name of the many-to-many manager on the relation

    If the sender is a subclass of ``ObjectSet``, only the ``set_manager``
    must be defined.
    """
    scope = instance
    try:
        objectset = getattr(scope, kwargs['set_name'])
    except ObjectDoesNotExist:
        return

    objectset_manager = getattr(objectset, kwargs['set_manager'])
    oids = set(objectset_manager.distinct().values_list('id', flat=True))
    nids = set(scope.get_queryset().distinct().values_list('id', flat=True))

    added = (oids | nids) - oids
    removed = (oids | nids) - nids

    if added:
        objectset_manager.add(*added)
    if removed:
        objectset_manager.remove(*removed)

def objectset_incr_count_pre_save(instance, action, pk_set, **kwargs):
    """Handlers syncing `count` based on the number of objects are being
    added or removed from the m2m relationship.
    """
    if action in ('pre_add', 'pre_remove', 'pre_clear'):
        if action == 'pre_clear':
            count = -instance.count
        else:
            count = len(pk_set)
            if action == 'pre_remove':
                count = -count

        instance.count += count
        instance.save()


