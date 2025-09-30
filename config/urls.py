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
    url=settings.SWAGGER_SETTINGS.get("DEFAULT_API_URL"),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # 앱 API
    path("api/products/", include("apps.products.urls")),
    path("api/admin/products/", include(("apps.products.admin_urls", "products_admin"), namespace="products_admin")),
    path("api/user/", include("apps.users.urls")),
    path("api/admin/users/", include("apps.users.admin_urls")),
    path("api/orders/", include("apps.orders.urls")),
    path("api/admin/orders/", include("apps.orders.admin_urls")),
    path("api/cart/", include("apps.carts.urls")),
    path("api/payments/", include("apps.payments.urls.user_urls")),
    path("api/admin/payments/", include("apps.payments.urls.admin_urls")),
    path("api/", include("apps.stats.urls")),
    path("api/support/", include("apps.support.urls")),
    path("api/admin/support/", include("apps.support.admin_urls")),
    # Swagger 문서 (TODO : 개발 완료 후 DEBUG 설정으로 이동)
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # 인증
    path("accounts/", include("django.contrib.auth.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
