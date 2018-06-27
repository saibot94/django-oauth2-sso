from __future__ import absolute_import

from django.http.response import Http404
from django.utils.http import urlencode
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect

from django.http import HttpResponse

from django.urls import reverse
from django.conf import settings

from .backends import import_from

from oauth2_sso.helpers import get_django_setting_or_default


@require_http_methods(["GET"])
def authenticate_code(request):
    oauth_settings = get_django_setting_or_default('OAUTH', dict())
    code = request.GET.get('code')
    if code is None:
        raise Http404('Code should have been present in request')
    else:
        user = authenticate(request=request, code=code)
        if user:
            login(request, user)
            if 'USER_POST_LOGIN_INIT' in oauth_settings:
                import_from(oauth_settings['USER_POST_LOGIN_INIT'])(request)
            if 'next' in request.session and request.session['next']:
                redir_url = request.session['next']
                del request.session['next']
                return redirect(redir_url)
            login_complete_redirect = oauth_settings['LOGIN_COMPLETE_REDIRECT'] if 'LOGIN_COMPLETE_REDIRECT' in oauth_settings else '/'
            return redirect(login_complete_redirect)
        else:
            print("Not logged in, redirecting")
            alternate_login = get_django_setting_or_default('ALTERNATE_LOGIN_URL', '/')
            return redirect(alternate_login)


def redirect_to_login(request):
    oauth_settings = get_django_setting_or_default('OAUTH', dict())
    auth_url = oauth_settings['AUTHORIZATION_URL'] if 'AUTHORIZATION_URL' in oauth_settings else None
    if not auth_url:
        content = '''
        <h2>An error has occured</h2>
        <p>One or more required parameters from the OAUTH config objects are missing. Please check if this is the case</p>
        '''
        return HttpResponse(content, status=500)
    else:
        data = {
            'scope': 'read:user',
            'response_type': 'code',
            'redirect_uri': oauth_settings['REDIRECT_URI'] if 'REDIRECT_URI' in oauth_settings else None,
            'client_id': oauth_settings['CLIENT_ID'] if 'CLIENT_ID' in oauth_settings else None
        }
        if 'next' in request.GET:
            request.session['next'] = request.GET['next']
        return redirect(auth_url + '?' + urlencode(data))
