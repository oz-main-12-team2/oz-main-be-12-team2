from django.urls import path

from . import views
from .social_views import GoogleLoginCallbackView, GoogleLoginStartView, NaverLoginCallbackView, NaverLoginStartView

urlpatterns = [
    path("register/", views.register, name="user_register"),
    path("login/", views.login, name="user_login"),
    path("logout/", views.logout, name="user_logout"),
    path("me/", views.user_profile, name="user_profile"),
    path("me/delete/", views.user_delete, name="user_delete"),
    path("change-password/", views.change_password, name="user_change_password"),
    # 소셜 로그인
    path("login/naver/", NaverLoginStartView.as_view(), name="naver_login_start"),
    path("login/naver/callback/", NaverLoginCallbackView.as_view(), name="naver_login_callback"),
    path("login/google/", GoogleLoginStartView.as_view(), name="google_login_start"),
    path("login/google/callback/", GoogleLoginCallbackView.as_view(), name="google_login_callback"),
    # 비밀번호 재설정
    path("activate/<uidb64>/<token>/", views.activate_user, name="user_activate"),
    path("password-reset/request/", views.password_reset_request, name="password_reset_request"),
    path("password-reset/confirm/<uidb64>/<token>/", views.password_reset_confirm, name="password_reset_confirm"),
]
