from django.conf.urls.defaults import *

urlpatterns = patterns('mako.fields.views',
    url(r'^$', 'fetch_cached_fields', name='mako-cached-fields'),
    url(r'^save/$', 'save_cached_fields', name='mako-save-cached-fields'),
    url(r'^(?P<field_id>\d+)/$', 'render_field', name='mako-render-field'),
    url(r'^(?P<field_id>\d+)/validate/$', 'validate_field',
        name='mako-validate-field'),
    url(r'^search/$', 'search', name='mako-search-fields'),
)
