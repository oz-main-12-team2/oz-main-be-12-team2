from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrderViewSet

router = DefaultRouter()
router.register(r"order", OrderViewSet, basename="order")  # prefix와 basename 변경

urlpatterns = [
    path("", include(router.urls)),
]
