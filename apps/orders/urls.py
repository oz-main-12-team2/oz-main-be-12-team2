from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrderViewSet

app_name = "order"  # ✅ reverse() 호출 시 namespace로 사용 가능

# DefaultRouter 생성
router = DefaultRouter()
router.register(r"", OrderViewSet, basename="order")  # ✅ URL prefix를 빈 문자열로 설정

# urlpatterns에 router.urls 포함
urlpatterns = [
    path("", include(router.urls)),
]
