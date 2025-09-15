from django.urls import path

from . import admin_views

urlpatterns = [
    path("", admin_views.admin_user_list, name="admin_user_list"),
    path("<int:user_id>/", admin_views.AdminUserDetailView.as_view(), name="admin_user_detail"),
]
