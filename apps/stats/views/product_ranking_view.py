from datetime import datetime

from django.db.models import F, Sum
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.orders.models import OrderItem
from apps.stats.serializers import ProductRankingResponseSerializer


class ProductRankingAPIView(GenericAPIView):
    """
    상품 판매 랭킹 (일간 판매량 기준 Top 10)
    GET /api/stats/rankings
    """

    permission_classes = [AllowAny]
    serializer_class = ProductRankingResponseSerializer
    pagination_class = None  # 페이지네이션 비활성화
    filter_backends = []  # ordering filter 비활성화

    def get(self, request, *args, **kwargs):
        today = datetime.today().date()

        qs = (
            OrderItem.objects.filter(order__created_at__date=today)
            .values("product_id")  # ✅ product 기준으로 그룹화
            .annotate(
                name=F("product__name"),
                category=F("product__category"),
                author=F("product__author"),
                description=F("product__description"),
                publisher=F("product__publisher"),
                image=F("product__image"),
                quantity=Sum("quantity"),
                revenue=Sum("total_price"),
            )
            .order_by("-quantity")[:10]
        )

        rankings = [
            {
                "rank": idx + 1,
                "product_id": item["product_id"],
                "name": item["name"],
                "category": item["category"],
                "author": item["author"],
                "description": item["description"],
                "publisher": item["publisher"],
                "image": item["image"],
                "quantity": item["quantity"],
                "revenue": item["revenue"],
            }
            for idx, item in enumerate(qs)
        ]

        data = {"period": str(today), "rankings": rankings}

        serializer = self.get_serializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)
