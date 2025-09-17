from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet

router = DefaultRouter()
router.register(r"", OrderViewSet, basename="order")  # ✅ prefix를 빈 문자열로 변경

app_name = "order"

urlpatterns = [
    path("", include(router.urls)),
]
