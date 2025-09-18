from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Project API",
        default_version="v1",
        description="API 문서",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # 앱 API
    path("api/product/", include("apps.products.urls")),
    path("api/admin/product/", include(("apps.products.admin_urls", "products_admin"), namespace="products_admin")),
    path("api/user/", include("apps.users.urls")),
    path("api/admin/user/", include("apps.users.admin_urls")),
    path("api/order/", include("apps.orders.urls")),  # ✅ config에서 api/order/로 감싸기
    path("api/cart/", include("apps.carts.urls")),
    path("api/payment/", include("apps.payments.urls")),
    path("api/admin/payment/", include("apps.payments.admin_urls")),
    # Swagger 문서
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # 인증
    path("accounts/", include("django.contrib.auth.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
