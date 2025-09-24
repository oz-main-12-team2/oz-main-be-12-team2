from django.urls import path

from .views import DashboardAPIView, ProductRankingAPIView

urlpatterns = [
    path("dashboard/", DashboardAPIView.as_view(), name="admin-dashboard"),
    path("rankings/", ProductRankingAPIView.as_view(), name="product-ranking"),
]
