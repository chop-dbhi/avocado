from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # authentication    
    url(r'^login/$', 'avocado.contrib.client.views.login',
        {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),

    url(r'^define/$', 'avocado.contrib.client.views.define', name='define'),
    url(r'^report/$', 'avocado.contrib.client.views.report', name='report'),
)
