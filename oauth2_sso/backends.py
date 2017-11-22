from importlib import import_module

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Group
import requests

UserModel = get_user_model()


def import_from(full_name):
    module_name, function_name = full_name.rsplit('.', 1)
    mod = import_module(module_name)
    return getattr(mod, function_name)


def _get_oauth_setting_or_none(setting_name):
    if setting_name in settings.OAUTH:
        return settings.OAUTH[setting_name]
    else:
        return None


class OAuth2Backend(ModelBackend):
    # OAuth stuff
    CLIENT_ID = _get_oauth_setting_or_none('CLIENT_ID')
    GRANT_TYPE = _get_oauth_setting_or_none('GRANT_TYPE')
    CLIENT_SECRET = _get_oauth_setting_or_none('CLIENT_SECRET')
    REDIRECT_URI = _get_oauth_setting_or_none('REDIRECT_URI')
    USER_INFO_URL = _get_oauth_setting_or_none('USER_INFO_URL')
    TOKEN_URL = _get_oauth_setting_or_none('TOKEN_URL')
    # User definition stuff (optional)
    USER_GROUPS_URL = _get_oauth_setting_or_none('USER_GROUPS_URL')
    GROUP_EXTRACTION_FUNCTION = _get_oauth_setting_or_none('GROUP_EXTRACTION_FUNCTION')
    USER_CREATION_FUNCTION = _get_oauth_setting_or_none('USER_CREATION_FUNCTION')
    USER_GROUP_MAPPINGS = _get_oauth_setting_or_none('USER_GROUP_MAPPINGS')
    USER_FIELD_MAPPINGS = _get_oauth_setting_or_none('USER_FIELD_MAPPINGS')
    USERNAME_FIELD = _get_oauth_setting_or_none('USERNAME_FIELD')

    def __init__(self):
        self.access_token = None
        self.request = None

    def authenticate(self, request=None, code=None, **kwargs):
        if code is None or request is None:
            return None
        self.request = request
        data = {
            'code': code,
            'grant_type': self.GRANT_TYPE,
            'client_secret': self.CLIENT_SECRET,
            'client_id': self.CLIENT_ID,
            'redirect_uri': self.REDIRECT_URI
        }
        auth_response = requests.post(self.TOKEN_URL, data=data)
        if auth_response.status_code == 200:
            print('Successfully logged in user')
        else:
            self._err(auth_response)
            return None

        request.session['access_token'] = self.access_token = auth_response.json()['access_token']
        user = self.setup_user()
        if user is not None and self.USER_GROUPS_URL and self.GROUP_EXTRACTION_FUNCTION:
            self.setup_user_groups(user)
        if user is not None and self.USER_CREATION_FUNCTION:
            user_creation_fct = import_from(self.USER_CREATION_FUNCTION)
            user = user_creation_fct(self.request, user)
        return user

    def setup_user(self):
        user_info_response = requests.get(self.USER_INFO_URL,
                                          headers={'Authorization': 'Bearer ' + self.access_token})
        user_info = user_info_response.json()
        return self.get_or_create_user(user_info)

    def configure_user(self, user, user_info):
        for mapping in self.USER_FIELD_MAPPINGS:
            setattr(user, mapping[0], user_info[mapping[1]])
        user.save(update_fields=list(map(lambda x: x[1], self.USER_FIELD_MAPPINGS)))
        return user

    def get_or_create_user(self, user_info):
        try:
            user = UserModel._default_manager.get_by_natural_key(user_info[self.USERNAME_FIELD])
            return self.configure_user(user, user_info)
        except UserModel.DoesNotExist:
            user, created = UserModel._default_manager.get_or_create(
                **{UserModel.USERNAME_FIELD: user_info[self.USERNAME_FIELD]})
            if created:
                return self.configure_user(user, user_info)

    def setup_user_groups(self, user):
        user_groups_response = requests.get(self.USER_GROUPS_URL,
                                            headers={'Authorization': 'Bearer ' + self.access_token})
        if user_groups_response.status_code == 200:
            groups = import_from(self.GROUP_EXTRACTION_FUNCTION)(self.request, user, user_groups_response.json())
            # get groups that were received in the response
            parsed_groups = filter(lambda x: x[0] in groups,
                                   self.USER_GROUP_MAPPINGS)
            for group in parsed_groups:
                for domain_group in group[1]:
                    g = Group.objects.get(name=domain_group)
                    g.user_set.add(user)
                    user.save()
                    g.save()

    @staticmethod
    def _err(r):
        print('Error: {} - {}'.format(r.status_code, r.json()))
