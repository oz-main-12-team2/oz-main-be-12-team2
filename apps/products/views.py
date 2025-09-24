from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .filters import ProductFilter
from .models import Product
from .pagination import ProductPagination
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # django-filter 적용
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ProductFilter

    # 정렬 허용 필드
    ordering_fields = ["name", "price", "author", "category"]
    ordering = ["name"]  # 기본 정렬 (이름 순)

    pagination_class = ProductPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "query",
                openapi.IN_QUERY,
                description="전체 검색 (상품명, 설명, 저자, 카테고리 포함)",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter("name", openapi.IN_QUERY, description="상품명", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter(
                "description", openapi.IN_QUERY, description="상품 설명", type=openapi.TYPE_STRING, required=False
            ),
            openapi.Parameter(
                "author", openapi.IN_QUERY, description="저자명", type=openapi.TYPE_STRING, required=False
            ),
            openapi.Parameter(
                "category", openapi.IN_QUERY, description="카테고리", type=openapi.TYPE_STRING, required=False
            ),
            openapi.Parameter(
                "min_price", openapi.IN_QUERY, description="최소 가격", type=openapi.TYPE_NUMBER, required=False
            ),
            openapi.Parameter(
                "max_price", openapi.IN_QUERY, description="최대 가격", type=openapi.TYPE_NUMBER, required=False
            ),
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                description="정렬 기준",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
