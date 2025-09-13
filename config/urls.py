from django.contrib import admin
from django.urls import include, path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.conf.urls.static import static

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
    path("api/admin/product/", include("apps.products.admin_urls")),
    path("api/user/", include("apps.users.urls")),
    path("api/admin/user/", include("apps.users.admin_urls")),
    path("api/orders/", include("apps.orders.urls")),

    # Swagger 문서 (로그인 없이 테스트)
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),

    path("accounts/", include("django.contrib.auth.urls")),
]

# 개발 환경에서 static 파일 서빙
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
