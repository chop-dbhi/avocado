from django.conf.urls.defaults import *

urlpatterns = patterns('avocado.columns.views',
    url(r'^search/$', 'search', name='column-search'),
)
