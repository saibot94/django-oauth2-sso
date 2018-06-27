from __future__ import absolute_import

from django.http.response import HttpResponseRedirect, HttpResponse
from django.test import TestCase, Client, override_settings
from django.contrib.auth.admin import User
import mock
import requests
import logging 

from django.conf import settings

from oauth2_sso.helpers import get_django_setting_or_default

MOCK_USER_DATA = {"username": "user1", "email": 'email@example.com', 'first_name': 'User'}


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    if args[0] == 'http://user.info.url.com':
        return MockResponse(MOCK_USER_DATA, 200)

    return MockResponse(None, 404)


def mocked_requests_post(*args, **kwargs):
    if args[0] == 'http://token.com':
        return MockResponse({"access_token": "1234"}, 200)

    return MockResponse(None, 404)


class OAuth2BackendTest(TestCase):
    def test_import_from(self):
        from oauth2_sso.backends import import_from
        import types
        func = import_from('oauth2_sso.backends.import_from')
        self.assertIs(True, isinstance(func, types.FunctionType), "The imported variable should be a function")
        self.assertIs(True, import_from == func, "The function imported should be the same")

    def test_login_redirect(self):
        resp = self.client.get('/login/')
        self.assertTrue(resp.url.startswith('https://example.com?'))
        self.assertTrue("scope=read%3Auser" in resp.url)
        self.assertTrue("redirect_uri=https%3A%2F%2Ftest-django-app.com" in resp.url)
        self.assertTrue("response_type=code" in resp.url)
        self.assertTrue("client_id=client" in resp.url)
        self.assertIs(True, isinstance(resp, HttpResponseRedirect))

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    @mock.patch('requests.post', side_effect=mocked_requests_post)
    def test_login(self, mock_post, mock_get):
        resp = self.client.get('/complete/?code=1234')
        self.assertIs(True, '1234' == self.client.session['access_token'])
        created_user = User.objects.get(username='user1')
        self.assertIs(True, 'email@example.com' == created_user.email)
        self.assertIs(True, 'user1' == created_user.username)
        self.assertIs(True, 'User' == created_user.first_name)

    @override_settings()
    def test_login_error_response_misconfigured(self):
        del settings.OAUTH
        resp = self.client.get('/login/')
        self.assertTrue(isinstance(resp, HttpResponse))
        self.assertEqual(500, resp.status_code)


class HelperTest(TestCase):

    @override_settings()
    def test_no_oauth_setting(self):
        del settings.OAUTH
        self.assertTrue(get_django_setting_or_default('OAUTH', 'TEST') == 'TEST')
    
    def test_with_oauth_seting(self):
        self.assertFalse(get_django_setting_or_default('OAUTH', 'TEST') == 'TEST')
