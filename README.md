# Django Oauth2 Client and User Configuration

[![Travis CI build status](https://travis-ci.org/saibot94/django-oauth2-sso.svg?branch=master)](https://travis-ci.org/saibot94/django-oauth2-sso)

## Motivation

SSO can be a tricky thing to setup, especially if your organization has a custom OAuth2 SSO provider that
returns information about users in a way uncompatible with the Django philosophy. 

This plugin allows you
to define custom callbacks that map the user and group details obtained from the authority to your Django
user model. You get a quick and easy way to programatically create users with the correct permissions once 
they are authenticated, freeing you of the burden of manually creating users from the admin tool.

## Installation

In order to install the package in your local repository, just run the following command:

`python setup.py install`

## Setting up in your app
In order to use this Django app, the following steps must be done:

Step 1: Add the auth backend and the installed app in the configuration file:

```python
INSTALLED_APPS = [
   # ...
    'oauth2_sso'
   # ...
]
```

```python
AUTHENTICATION_BACKENDS = [
# ...
'oauth2_sso.backends.OAuth2Backend'
# ...
]

```

Step 2:  Add the oauth urls to the root website:

```python
urlpatterns = [
    # ...
    url(r'^oauth/', include('oauth2_sso.urls')),
    # ...
]
```
Step 3: Add the LOGIN_URL and corresponding OAUTH config object for your application. Example:

```python
LOGIN_URL = "/oauth/login/" # different from your ModelBackend auth

OAUTH = {
    'CLIENT_ID': 'my-id',
    'AUTHORIZATION_URL': '<auth_url>',
    'REDIRECT_URI': '<app_redirect_url>', # should end with /oauth/complete (the view is provided by this app)
    'CLIENT_SECRET': '<secret>',
    'LOGIN_COMPLETE_REDIRECT': '/some/url/in/your/app',
    'TOKEN_URL': '<returns_access_token>',
    'GRANT_TYPE': 'authorization_code',

     # User config (required)
    'USER_INFO_URL': '<authenticated API for getting user info>',
    'USERNAME_FIELD': 'username',
    'USER_FIELD_MAPPINGS': [('username','username'), ('email','email'),('first_name', 'first_name'),('last_name','last_name')],
    
    # User config (optional)
    'USER_CREATION_FUNCTION': 'path.to.extra_user_creation_function', # any function in pythonpath
    'GROUP_EXTRACTION_FUNCTION': 'ptah.to.group_extraction_fct', # any function in pythonpath
    'USER_GROUP_MAPPINGS': [('it-dep-di-cso', ['Event reporters', 'Incident handlers', 'Incident viewers'])],
    'USER_GROUPS_URL': '<group_info_api>',
    'USER_POST_LOGIN_INIT': 'some.path.init_session'
}

```

## Configuration 

This section explains what the different config options do and which are mandatory.

### OAuth related configs:

- LOGIN_COMPLETE_REDIRECT - a Django URL that will be resolved based on your application. The 
login will redirect you to this URL once the user has successfully logged in
- GRANT_TYPE - what kind of grant type to pass to the auth server

### Mandatory user creation flow related configs:

- USER_INFO_URL - the secure URL from which to get the user details, once receiving the authentication 
token from the server.
- USERNAME_FIELD - the user name field of your User model, can be any custom model that you defined in your app
- USER_FIELD_MAPPINGS - at least all mandatory user fields should be placed here. 
This is a list of tuples, mapping from the JSON object that you get from calling the USER_INFO_URL with "Authorization: 
Bearer < token >" and the Django user model that you've defined 


### Optional user creation flow related configs:

- USER_CREATION_FUNCTION - once the user login is successful, there may be a need to add extra
user information or create extra objects for the user. The function receives the request and 
user object. The modified user is returned.
- GROUP_EXTRACTION_FUNCTION - if the *USER_GROUPS_URL* is defined, this function is loaded and used to parse
the response from the groups url. It should return a list of strings, defining the groups to which the user
belongs in the SSO authority.
- USER_GROUP_MAPPINGS - if the USER_GROUPS_URL and extraction function are defined, the backend looks up 
all the SSO groups that the user belongs to and maps that user to the list of groups defined by the second
parameter in the tuple (application groups).
- USER_GROUPS_URL  - url linking to the secure groups endpoint
- USER_POST_LOGIN_INIT - after the user is created and assigned groups, some extra things might be needed
to be added to the session or request object. Use this custom callback for those purposes.


## Usage

Once you try to access some endpoint that has the `@login_required` decorator on top of it, 
you'll be redirected to the organization login URI that you defined and can authenticate there
using the tools provided. Upon successful authentication the user urls are called and the callbacks are used
to shape your user into the form that you've provided.

## TODO
- Implement logout endpoint and config.
- Suggestions are welcome, just open an issue.
## License

MIT
