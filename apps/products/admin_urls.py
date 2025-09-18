from django.urls import path

from . import admin_views, stats_views

urlpatterns = [
    # 상품 생성
    path("create/", admin_views.admin_product_create, name="admin_product_create"),
    # 상품 상세조회 / 수정 / 삭제 (pk 공통)
    path("<int:pk>/", admin_views.admin_product_detail_update_delete, name="admin_product_detail_update_delete"),
    # 상품 통계
    path("statistics/", stats_views.ProductSalesStatisticsAPIView.as_view(), name="product_sales_statistics"),
    # 재고 총량
    path(
        "stocks",
        stats_views.ProductStockAPIView.as_view(),
        name="product-stocks",
    ),
]
