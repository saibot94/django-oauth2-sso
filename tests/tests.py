from django.http.response import HttpResponseRedirect
from django.test import TestCase, Client
from django.contrib.auth.admin import User
import mock
import requests

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
        self.assertIs(True,
                      resp.url == 'https://example.com?scope=read%3Auser&redirect_uri=https%3A%2F%2Ftest-django-app.com'
                                  '&response_type=code&client_id=client')
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