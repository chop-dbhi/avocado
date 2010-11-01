import os
import sys

from django.conf import settings
from django.db.models import get_app
from django.db.models.signals import post_syncdb
from django.db import connections, transaction, DEFAULT_DB_ALIAS

def load_custom_sql(app, created_models, verbosity=2, **kwargs):
    app_dir = os.path.normpath(os.path.join(os.path.dirname(app.__file__), 'sql'))
    backend = settings.DATABASES[DEFAULT_DB_ALIAS]['ENGINE'].split('.')[-1]

    custom_files = (os.path.join(app_dir, "custom.%s.sql" % backend),
                    os.path.join(app_dir, "custom.sql"))

    for custom_file in custom_files:
        if os.path.exists(custom_file):
            print "Loading customized SQL for %s" % app.__name__
            fp = open(custom_file, 'U')
            cursor = connections['default'].cursor()
            try:
                cursor.execute(fp.read().decode(settings.FILE_CHARSET))
            except Exception:
                sys.stderr.write("Couldn't execute custom SQL for %s" % app.__name__)
                import traceback
                traceback.print_exc()
                transaction.rollback_unless_managed()
            else:
                transaction.commit_unless_managed()

post_syncdb.connect(load_custom_sql, sender=get_app('avocado'))
