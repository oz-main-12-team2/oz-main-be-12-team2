# admin_urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .admin_views import AdminOrderViewSet

app_name = "admin_orders"

router = DefaultRouter()
router.register(r"", AdminOrderViewSet, basename="admin-order")

urlpatterns = [
    path("", include(router.urls)),
]
