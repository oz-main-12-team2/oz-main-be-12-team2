from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrderViewSet

app_name = "orders"  # namespace 이름 수정

router = DefaultRouter()
router.register(r"", OrderViewSet, basename="order")

urlpatterns = [
    path("", include(router.urls)),
]
