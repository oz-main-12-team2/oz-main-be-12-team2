from django.urls import path
from . import admin_views

urlpatterns = [
    path('users/', admin_views.admin_user_list, name='admin_user_list'),
    path('user/<int:user_id>/', admin_views.admin_user_detail, name='admin_user_detail'),
    path('user/<int:user_id>/', admin_views.admin_user_update, name='admin_user_update'),
    path('user/<int:user_id>/', admin_views.admin_user_delete, name='admin_user_delete'),
]