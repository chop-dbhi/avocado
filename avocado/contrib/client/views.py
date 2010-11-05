import re

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
# Avoid shadowing the login() view below.
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.views.decorators.cache import never_cache

from django.template import Template, Context
from django.core.cache import cache
from django.core.mail import mail_admins
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext

from avocado.contrib.server.api.handlers import (CategoryHandler,
    CriterionHandler, ColumnHandler)
from avocado.contrib.client.utils import get_ip_address

MAX_LOGIN_ATTEMPTS = 10
LOGIN_CACHE_TIMEOUT = 60 * 60 # 1 hour
LOGIN_ATTEMPT_KEY = 'auth_attempts_%s_%s'
LOGIN_ATTEMPT_FAIL_SUBJECT = 'Failed Login Attempt'
LOGIN_ATTEMPT_FAIL_MESSAGE = """
The max login attempts for username "{{ username }}" with the IP
address "{{ ip }}" has been reached.

{% if exists %}
This user's account has been deactivated.
{% else %}
No account exists for this username. The user/attacker has been suspended
for {{ timeout }} hour(s) from the last attempt made.
{% endif %}
"""

@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm):
    """Displays the login form and handles the login action."""

    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        # get username and ip to test against
        username = request.POST['username']
        password = request.POST['password']

        ip = get_ip_address(request)
        key = LOGIN_ATTEMPT_KEY % (username, ip)

        value = cache.get(key) or 0
        num_attempts = value + 1

        # process view as normal as long as the max attempts has not been
        # reached
        if num_attempts < MAX_LOGIN_ATTEMPTS:
            form = authentication_form(data=request.POST)

            if form.is_valid():
                # Light security check -- make sure redirect_to isn't garbage.
                if not redirect_to or ' ' in redirect_to:
                    redirect_to = settings.LOGIN_REDIRECT_URL

                # Heavier security check -- redirects to http://example.com should
                # not be allowed, but things like /view/?param=http://example.com
                # should be allowed. This regex checks if there is a '//' *before* a
                # question mark.
                elif '//' in redirect_to and re.match(r'[^\?]*//', redirect_to):
                        redirect_to = settings.LOGIN_REDIRECT_URL

                # Okay, security checks complete. Log the user in.
                auth_login(request, form.get_user())

                if request.session.test_cookie_worked():
                    request.session.delete_test_cookie()

                return HttpResponseRedirect(redirect_to)
        else:
            # once the max attempts has been reached, deactive the account
            # and email the admins
            if num_attempts == MAX_LOGIN_ATTEMPTS:
                exists = True
                try:
                    user = User.objects.get(username=username)
                    user.is_active = False
                    user.save()
                except User.DoesNotExist:
                    exists = False

                t = Template(LOGIN_ATTEMPT_FAIL_MESSAGE)
                c = Context({
                    'exists': exists,
                    'username': username,
                    'ip': ip,
                    'timeout': int(LOGIN_CACHE_TIMEOUT / 3600.0)
                })

                mail_admins(LOGIN_ATTEMPT_FAIL_SUBJECT, t.render(c), True)


            data = {'username': username, 'password': ' '*len(password)}
            form = authentication_form(data=data)
            form.is_valid()

        cache.set(key, num_attempts, LOGIN_CACHE_TIMEOUT)

    else:
        form = authentication_form(request)

    request.session.set_test_cookie()

    return render_to_response(template_name, {
        'form': form,
        redirect_field_name: redirect_to,
    }, context_instance=RequestContext(request))


def define(request):
    categories = CategoryHandler().read(request)
    criteria = CriterionHandler().read(request)

    return render_to_response('define.html', {
        'categories': categories,
        'criteria': criteria,
    }, context_instance=RequestContext(request))

def report(request):
    columns = ColumnHandler().read(request)
    return render_to_response('report.html', {
        'columns': columns,
    }, context_instance=RequestContext(request))
