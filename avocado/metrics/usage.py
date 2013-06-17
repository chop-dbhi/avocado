import logging
from datetime import datetime
from threading import Thread
from django.contrib.contenttypes.models import ContentType
from .models import Log

logger = logging.getLogger(__name__)


def _log(instance=None, model=None, **kwargs):
    if instance:
        kwargs['content_object'] = instance
    elif model:
        kwargs['content_type'] = ContentType.objects.get_for_model(model)

    try:
        message = Log(**kwargs)
        message.save()
    except Exception as e:
        logger.exception('Error logging usage')


def log(event, async=True, **kwargs):
    """Log an event with an optional associated object.

    If `instance` is present, the generic `content_object` will be set. Other
    if just the model is provided, the content type will be associated.

    If a `request` object is supplied, the `user` and/or `session_key` will
    be extracted from it.

    By default the call will be executed in a thread to not block the current
    executing thread.
    """
    kwargs['event'] = event

    if 'request' in kwargs:
        request = kwargs.pop('request')
        if hasattr(request, 'user'):
            kwargs['user'] = request.user
        if hasattr(request, 'session'):
            kwargs['session_key'] = request.session.session_key

    # Set the timestamp now to prevent delay due to a blocked thread
    if 'timestamp' not in kwargs:
        kwargs['timestamp'] = datetime.now()

    if async:
        thread = Thread(target=_log, kwargs=kwargs)
        thread.start()
    else:
        _log(**kwargs)
