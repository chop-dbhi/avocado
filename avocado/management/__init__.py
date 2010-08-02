from django.db.models import get_app
from django.db.models.signals import post_syncdb

from avocado import signals

post_syncdb.connect(signals.load_custom_sql, sender=get_app('avocado'))
