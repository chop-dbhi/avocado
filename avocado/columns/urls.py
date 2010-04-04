from django.conf.urls.defaults import *

urlpatterns = patterns('mako.columns.views',
    url(r'^search/$', 'search', name='mako-search-columns'),
)
