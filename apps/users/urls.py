from allauth.socialaccount.providers.google.views import oauth2_login as google_oauth2_login
from allauth.socialaccount.providers.naver.views import oauth2_login as naver_oauth2_login
from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register, name="user_register"),
    path("login/", views.login, name="user_login"),
    path("logout/", views.logout, name="user_logout"),
    path("login/google/", google_oauth2_login, name="user_google_login"),
    path("login/naver/", naver_oauth2_login, name="user_naver_login"),
    path("me/", views.user_profile, name="user_profile"),
    path("me/delete/", views.user_delete, name="user_delete"),
    path("change-password/", views.change_password, name="user_change_password"),
]
