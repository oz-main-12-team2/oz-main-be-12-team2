from django.urls import path

from . import admin_views, stats_views

urlpatterns = [
    # URL: /api/admin/product/create
    path("create/", admin_views.admin_product_create, name="admin_product_create"),
    # URL: /api/admin/product/{product_id} (수정 및 상세 조회)
    # 뷰 함수명은 필요에 따라 admin_product_detail_and_update로 가정합니다.
    path("<int:pk>/", admin_views.admin_product_update, name="admin_product_update"),
    # URL: /api/admin/product/{product_id} (삭제)
    path(
        "<int:pk>/delete/",
        admin_views.admin_product_delete,
        name="admin_product_delete",
    ),
    # URL: /api/admin/product/statistics
    path("statistics/", stats_views.admin_sales_stats, name="admin_sales_stats"),
]


# 전체프로젝트 유알엘 이에요

# from django.contrib import admin
# from django.urls import path, include

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     # /api/admin/으로 시작하는 모든 요청을 products.urls로 라우팅
#     path('api/admin/', include('products.urls')),
# ]
