from django.conf.urls.defaults import *

urlpatterns = patterns('avocado.fields.views',
    url(r'^$', 'fetch_cached_fields', name='avocado-cached-fields'),
    url(r'^save/$', 'save_cached_fields', name='avocado-save-cached-fields'),
    url(r'^(?P<field_id>\d+)/$', 'render_field', name='avocado-render-field'),
    url(r'^(?P<field_id>\d+)/validate/$', 'validate_field',
        name='avocado-validate-field'),
    url(r'^search/$', 'search', name='avocado-search-fields'),
)
