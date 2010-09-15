from django.conf.urls.defaults import *
from piston.resource import Resource

from avocado.contrib.server.api.handlers import (CriterionHandler,
    CategoryHandler, ScopeHandler, PerspectiveHandler, ReportHandler,
    ReportResolverHandler)

criterion =  Resource(CriterionHandler)
category =  Resource(CategoryHandler)

# not yet exposed...
scope =  Resource(ScopeHandler)
perspective = Resource(PerspectiveHandler)
report = Resource(ReportHandler)
report_resolver = Resource(ReportResolverHandler)

category_patterns = patterns('',
    url(r'^$', category, name='read'),
    url(r'^(?P<id>\d+)/$', category, name='read'),
)

criterion_patterns = patterns('',
    url(r'^$', criterion, name='read'),
    url(r'^(?P<id>\d+)/$', criterion, name='read'),
)

# represents all of the `report` url patterns including
report_patterns = patterns('',
    url(r'^$', report, name='read'),

    # patterns relative to a particular saved instance
    url(r'^(?P<id>\d+)/', include(patterns('',
        url(r'^$', report, name='data'),
        url(r'^resolve/$', report_resolver, name='resolve'),
    ), namespace='stored')),
    
    # patterns relative to a temporary instance on the session
    url(r'^session/', include(patterns('',
        url(r'^$', report, {'id': 'session'}, name='data'),
        url(r'^resolve/$', report_resolver, {'id': 'session'}, name='resolve'),
    ), namespace='session'))
)

scope_patterns = patterns('',
    url(r'^$', scope, name='read'),
    url(r'^(?P<id>\d+)/$', scope, name='read'),
    url(r'^session/$', scope, {'id': 'session'}, name='session'),
)

perspective_patterns = patterns('',
    url(r'^$', perspective, name='read'),
    url(r'^(?P<id>\d+)/$', perspective, name='read'),
    url(r'^session/$', perspective, {'id': 'session'}, name='session'),
)

urlpatterns = patterns('',
    url(r'^criteria/', include(criterion_patterns, namespace='criteria')),
    url(r'^categories/', include(category_patterns, namespace='categories')),
    url(r'^reports/', include(report_patterns, namespace='reports')),
    url(r'^scope/', include(scope_patterns, namespace='scope')),
    url(r'^perspectives/', include(perspective_patterns, namespace='perspectives')),    
)
