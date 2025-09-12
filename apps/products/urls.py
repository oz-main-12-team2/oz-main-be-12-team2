from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    # URL: /product/
    path("", views.product_list, name="product_list"),
    # URL: /product/ranking
    path("ranking/", views.product_list, name="product_ranking"),
    # URL: /product/123 (pk 값을 정수로 받음)
    path("<int:pk>/", views.product_detail, name="product_detail"),
]


# 이거는 프로젝트네임유알엘

# from django.contrib import admin
# from django.urls import path, include

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     # /product/로 시작하는 모든 요청을 products.urls로 전달
#     path('product/', include('apps.products.urls')),
# ]
