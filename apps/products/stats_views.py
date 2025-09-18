# apps/products/stats_views.py
from datetime import datetime, timedelta

from django.db.models import Sum
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import OrderItem

from .models import Product
from .serializers import ProductSalesStatisticsSerializer


class ProductSalesStatisticsAPIView(APIView):
    """
    관리자 상품 판매 통계 조회
    GET /api/admin/products/statistics?date=2025-09-10
    """

    permission_classes = [permissions.IsAdminUser]  # ✅ 관리자 전용 접근 제한

    def get(self, request):
        date_str = request.query_params.get("date")
        try:
            if date_str:
                base_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            else:
                base_date = datetime.today().date()
        except ValueError:
            return Response(
                {
                    "success": False,
                    "error": "잘못된 요청 파라미터 (날짜 형식 오류)",
                    "code": "INVALID_DATE_FORMAT",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = OrderItem.objects.all()

        # 총 매출 (누적)
        total_revenue = qs.aggregate(total=Sum("total_price"))["total"] or 0

        # 오늘
        today_qs = qs.filter(order__created_at__date=base_date)
        today = {
            "quantity": today_qs.aggregate(q=Sum("quantity"))["q"] or 0,
            "revenue": today_qs.aggregate(r=Sum("total_price"))["r"] or 0,
        }

        # 이번주
        week_start = base_date - timedelta(days=base_date.weekday())
        week_end = week_start + timedelta(days=6)
        week_qs = qs.filter(order__created_at__date__range=[week_start, week_end])
        week = {
            "quantity": week_qs.aggregate(q=Sum("quantity"))["q"] or 0,
            "revenue": week_qs.aggregate(r=Sum("total_price"))["r"] or 0,
        }

        # 이번달
        month_qs = qs.filter(
            order__created_at__year=base_date.year,
            order__created_at__month=base_date.month,
        )
        month = {
            "quantity": month_qs.aggregate(q=Sum("quantity"))["q"] or 0,
            "revenue": month_qs.aggregate(r=Sum("total_price"))["r"] or 0,
        }

        # 최근 30일 추이
        last_30_days = [base_date - timedelta(days=i) for i in range(30)]
        trend = []
        for d in sorted(last_30_days):
            day_qs = qs.filter(order__created_at__date=d)
            trend.append(
                {
                    "date": d,
                    "quantity": day_qs.aggregate(q=Sum("quantity"))["q"] or 0,
                    "revenue": day_qs.aggregate(r=Sum("total_price"))["r"] or 0,
                }
            )

        data = {
            "total_revenue": total_revenue,
            "today": today,
            "week": week,
            "month": month,
            "trend": trend,
        }

        serializer = ProductSalesStatisticsSerializer(data)
        return Response({"success": True, "data": serializer.data, "message": "Success"})


class ProductStockAPIView(APIView):
    """
    관리자 전체 상품 재고 총합 조회
    GET /api/admin/products/stock
    """

    permission_classes = [permissions.IsAdminUser]  # ✅ 관리자 전용

    def get(self, request):
        try:
            total_stock = Product.objects.aggregate(total=Sum("stock"))["total"] or 0

            data = {"total_stock": total_stock}

            return Response(
                data,
                status=status.HTTP_200_OK,
            )

        except Exception:
            return Response(
                {
                    "message": "재고 정보를 불러올 수 없습니다.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
