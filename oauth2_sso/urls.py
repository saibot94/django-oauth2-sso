from __future__ import absolute_import

from django.conf.urls import url
from oauth2_sso import views

app_name = 'oauth2_sso'

urlpatterns = [
    url(r'^complete/', views.authenticate_code, name='auth_complete'),
    url(r'^login/', views.redirect_to_login, name='login')
]
