from datetime import datetime, timedelta

from django.db.models import Sum
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from apps.orders.models import Order, OrderItem
from apps.products.models import Product
from apps.stats.serializers import DashboardSerializer, ProductRankingResponseSerializer
from apps.users.models import User


class DashboardAPIView(GenericAPIView):
    """
    관리자 대시보드 통계 조회
    GET /api/admin/stats/dashboard
    """

    permission_classes = [IsAdminUser]
    serializer_class = DashboardSerializer  # ✅ 지정 가능

    def get(self, request, *args, **kwargs):
        base_date = datetime.today().date()

        total_users = User.objects.count()
        total_revenue = OrderItem.objects.aggregate(total=Sum("total_price"))["total"] or 0
        total_stock = Product.objects.aggregate(total=Sum("stock"))["total"] or 0
        today_orders = Order.objects.filter(created_at__date=base_date).count()

        today_qs = OrderItem.objects.filter(order__created_at__date=base_date)
        daily_sales = {
            "quantity": today_qs.aggregate(q=Sum("quantity"))["q"] or 0,
            "revenue": today_qs.aggregate(r=Sum("total_price"))["r"] or 0,
        }

        week_start = base_date - timedelta(days=base_date.weekday())
        week_end = week_start + timedelta(days=6)
        week_qs = OrderItem.objects.filter(order__created_at__date__range=[week_start, week_end])
        weekly_sales = {
            "quantity": week_qs.aggregate(q=Sum("quantity"))["q"] or 0,
            "revenue": week_qs.aggregate(r=Sum("total_price"))["r"] or 0,
        }

        month_qs = OrderItem.objects.filter(
            order__created_at__year=base_date.year,
            order__created_at__month=base_date.month,
        )
        monthly_sales = {
            "quantity": month_qs.aggregate(q=Sum("quantity"))["q"] or 0,
            "revenue": month_qs.aggregate(r=Sum("total_price"))["r"] or 0,
        }

        daily_trend = []
        for i in range(30):
            d = base_date - timedelta(days=i)
            qs = OrderItem.objects.filter(order__created_at__date=d)
            daily_trend.append(
                {
                    "date": d,
                    "quantity": qs.aggregate(q=Sum("quantity"))["q"] or 0,
                    "revenue": qs.aggregate(r=Sum("total_price"))["r"] or 0,
                }
            )
        daily_trend.reverse()

        data = {
            "total_users": total_users,
            "total_revenue": total_revenue,
            "total_stock": total_stock,
            "today_orders": today_orders,
            "daily_sales": daily_sales,
            "weekly_sales": weekly_sales,
            "monthly_sales": monthly_sales,
            "trend": daily_trend,
        }

        serializer = self.get_serializer(data)  # ✅ GenericAPIView 제공
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductRankingAPIView(GenericAPIView):
    """
    관리자 상품 판매 랭킹 (일간 판매량 기준 Top 10)
    GET /api/admin/stats/rankings/products
    """

    permission_classes = [IsAdminUser]
    serializer_class = ProductRankingResponseSerializer  # ✅ 전체 응답 구조를 반영

    def get(self, request, *args, **kwargs):
        today = datetime.today().date()

        qs = (
            OrderItem.objects.filter(order__created_at__date=today)
            .values("product_id", "product__name")
            .annotate(quantity=Sum("quantity"), revenue=Sum("total_price"))
            .order_by("-quantity")[:10]
        )

        rankings = [
            {
                "rank": idx + 1,
                "product_id": item["product_id"],
                "name": item["product__name"],
                "quantity": item["quantity"],
                "revenue": item["revenue"],
            }
            for idx, item in enumerate(qs)
        ]

        data = {"period": str(today), "rankings": rankings}

        serializer = self.get_serializer(data)  # ✅ ResponseSerializer 사용
        return Response(serializer.data, status=status.HTTP_200_OK)
