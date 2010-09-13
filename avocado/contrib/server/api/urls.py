from django.conf.urls.defaults import *
from piston.resource import Resource

from avocado.contrib.server.api.handlers import (CriterionHandler,
    CategoryHandler, ScopeHandler, PerspectiveHandler, ReportHandler)

criterion =  Resource(CriterionHandler)
category =  Resource(CategoryHandler)

# not yet exposed...
scope =  Resource(ScopeHandler)
perspective = Resource(PerspectiveHandler)
report = Resource(ReportHandler)

category_patterns = patterns('',
    url(r'^$', category, name='read'),
    url(r'^(?P<id>\d+)/$', category, name='read'),
)

criterion_patterns = patterns('',
    url(r'^$', criterion, name='read'),
    url(r'^(?P<id>\d+)/$', criterion, name='read'),
)

report_patterns = patterns('',
    url(r'^$', report, name='read'),
    url(r'^session/$', report, {'id': 'session'}, name='read'),
    url(r'^(?P<id>(\d+|session))/$', report, name='read'),
)

urlpatterns = patterns('',
    url(r'^criteria/', include(criterion_patterns, namespace='criteria')),
    url(r'^categories/', include(category_patterns, namespace='categories')),
)
