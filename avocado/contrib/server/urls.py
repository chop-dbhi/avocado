from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    url(r'^denied/', 'core.views.denied', name='denied'),
    # current API
    url(r'^api/', include('avocado.contrib.server.api.urls', namespace='api')),
    # versioned APIs
    url(r'^api/v1/', include('avocado.contrib.server.api.urls')),
)

if settings.DEBUG:
    media_url = settings.MEDIA_URL
    if media_url.startswith('/'):
        media_url = media_url[1:]
    urlpatterns += patterns('',
        url(r'^%s(?P<path>.*)$' % media_url, 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    )
    del media_url
