import re

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson

from avocado.models import Report, Scope, Perspective

class SessionReportMiddleware(object):
    def process_request(self, request):
        modified = False
        if not request.session.has_key('report'):
            modified = True
            report = Report()
            request.session['report'] = report
        else:
            report = request.session['report']
        
        if not report.scope_id:
            modified = True
            report.scope = Scope()
        if not report.perspective_id:
            modified = True
            report.perspective = Perspective()
        
        request.session.modified = modified

# dumb regex to extract the referer's path
extract_path = re.compile(r'^https?:\/\/[^\/]*(.*)$')

class BaseAuthMiddleware(object):
    def __init__(self):
        self.login_url = getattr(settings, 'LOGIN_URL')

    def _process_ajax_request(self, request):
        try:
            path = extract_path.match(request.META['HTTP_REFERER']).groups()[0]
            redirect = '%s?next=%s' % (self.login_url, path)
        except (AttributeError, IndexError):
            redirect = self.login_url
        return HttpResponse(simplejson.dumps({'redirect': redirect}),
            mimetype='application/json', status=302)

    def _process_request(self, request):
        redirect = '%s?next=%s' % (self.login_url, request.path)
        return HttpResponseRedirect(redirect)


class AuthNotRequiredMiddleware(BaseAuthMiddleware):
    def __init__(self):
        super(AuthNotRequiredMiddleware, self).__init__()
        self.urls = tuple([re.compile(url) for url in getattr(settings,
            'AUTH_NOT_REQUIRED_URLS', ())])

    def process_request(self, request):
        if request.user.is_authenticated():
            return        

        path = request.path.lstrip('/')
        for url in self.urls:
            if url.match(path):
                return

        if request.is_ajax():
            return self._process_ajax_request(request)
        return self._process_request(request)

class AuthRequiredMiddleware(BaseAuthMiddleware):
    def __init__(self):
        super(AuthNotRequiredMiddleware, self).__init__()
        self.urls = tuple([re.compile(url) for url in getattr(settings,
            'AUTH_REQUIRED_URLS', ())])

    def process_request(self, request):
        if request.user.is_authenticated():
            return

        path = request.path.lstrip('/')
        for url in self.urls:
            if url.match(path):
                if request.is_ajax():
                    return self._process_ajax_request(request)
                return self._process_request(request)
