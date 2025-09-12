from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.register, name='user_register'),
    path('login/', views.login, name='user_login'),
    path('logout/', views.logout, name='user_logout'),
    path('login/google/', views.google_login, name='user_google_login'),
    path('login/naver/', views.naver_login, name='user_naver_login'),
    path('me/', views.user_profile, name='user_profile'),
    path('me/delete/', views.user_delete, name='user_delete'),
    path('change-password/', views.change_password, name='user_change_password'),
]