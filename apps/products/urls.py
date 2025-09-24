# apps/products/urls.py

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ProductViewSet

app_name = "products"

router = DefaultRouter()
router.register(r"", ProductViewSet, basename="product")

urlpatterns = [
    path("", include(router.urls)),
]
