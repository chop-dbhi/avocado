import re
import subprocess

from django.conf import settings
from django import template

__all__ = ('svn_revision', 'hg_revision')

register = template.Library()

class SVNRevision(object):
    "Simple class to determine the current subversion rev."
    @property
    def revision(self):
        if not hasattr(self, '_revision'):
            self._revision = None

            if hasattr(settings, 'PROJ_DIR'):
                try:
                    f = subprocess.Popen(['svnversion', settings.PROJ_DIR], stdout=subprocess.PIPE).stdout
                except (OSError, ValueError):
                    return

                out = f.read().strip()
                m = re.search('(?:\d+:)?(\d+)[MS]?$', out)
                if m:
                    self._revision = m.group(1)
        return self._revision
_svn_revision = SVNRevision()


@register.simple_tag
def svn_revision():
    "Displays the HEAD revision number for subversion"
    return _svn_revision.revision and 'r%s' % (_svn_revision.revision or 'unavailable')


class HgRevision(object):
    "Simple class to determine the current mercurial rev."
    @property
    def revision(self):
        if not hasattr(self, '_revision'):
            self._revision = None          

            try:
                f = subprocess.Popen('hg log -l1 .'.split(), stdout=subprocess.PIPE).stdout
                out = f.read().strip()
                m = re.search('^changeset:\s+\d+:(\w+)\s.*', out)
                if m:
                    self._revision = m.group(1)                
            except (OSError, ValueError):
                pass
        return self._revision
_hg_revision = HgRevision()


@register.simple_tag
def hg_revision():
    "Displays the latest changeset for mercurial."
    return _hg_revision.revision and '%s' % (_hg_revision.revision or 'unavailable')
