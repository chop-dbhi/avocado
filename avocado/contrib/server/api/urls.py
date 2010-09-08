from django.conf.urls.defaults import *
from piston.resource import Resource

from avocado.contrib.server.api.handlers import CriterionHandler, CategoryHandler

criterion_handler = Resource(CriterionHandler)
category_handler = Resource(CategoryHandler)

category_patterns = patterns('',
    url(r'^$', category_handler, name='read'),
    url(r'^(?P<id>\d+)/$', category_handler, name='read'),
)

criterion_patterns = patterns('',
    url(r'^$', criterion_handler, name='read'),
    url(r'^(?P<id>\d+)/$', criterion_handler, name='read'),
)

urlpatterns = patterns('',
    url(r'^criteria/', include(criterion_patterns, namespace='criteria')),
    url(r'^categories/', include(category_patterns, namespace='categories')),
)
