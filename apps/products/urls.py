# apps/products/urls.py

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AdminProductViewSet, ProductViewSet

app_name = "products"

router = DefaultRouter()
router.register(r"admin/products", AdminProductViewSet, basename="admin-product")
router.register(r"products", ProductViewSet, basename="product")

urlpatterns = [
    path("", include(router.urls)),
]
