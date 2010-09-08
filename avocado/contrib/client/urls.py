from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # authentication    
    url(r'^login/$', 'django.contrib.auth.views.login',
        {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),

    url(r'^design/$', 'avocado.contrib.client.views.design', name='design'),
    url(r'^report/$', 'avocado.contrib.client.views.report', name='report'),
)
