import os
import sys

from django.db.models import signals
from django.db import connection, transaction
from django.conf import settings

def load_customized_sql(app, created_models, verbosity=2, **kwargs):
    app_dir = os.path.normpath(os.path.join(os.path.dirname(app.__file__), 'sql'))
    custom_files = [os.path.join(app_dir, 'custom.%s.sql' % settings.DATABASE_ENGINE),
                    os.path.join(app_dir, 'custom.sql')]
    for custom_file in custom_files: 
        if os.path.exists(custom_file):
            print 'Loading customized SQL for %s' % app.__name__
            fp = open(custom_file, 'U')
            cursor = connection.cursor()
            try:
                cursor.execute(fp.read().decode(settings.FILE_CHARSET))
            except Exception:
                sys.stderr.write('Couldn not execute custom SQL for %s' % app.__name__)
                import traceback
                traceback.print_exc()
                transaction.rollback_unless_managed()
            else:
                transaction.commit_unless_managed()
        
signals.post_syncdb.connect(load_customized_sql)