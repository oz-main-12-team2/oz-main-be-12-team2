from django.urls import path

from .views.admin_dashboard_view import DashboardAPIView
from .views.product_ranking_view import ProductRankingAPIView

urlpatterns = [
    path("admin/stats/dashboard/", DashboardAPIView.as_view(), name="admin-dashboard"),
    path("stats/rankings/", ProductRankingAPIView.as_view(), name="product-ranking"),
]
