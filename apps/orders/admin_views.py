# admin_views.py
from django.db.models import Sum
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from ..orders.models import Order, OrderItem
from ..orders.serializers import OrderSerializer


class AdminOrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]

    http_method_names = ["get", "post", "put", "patch", "delete"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Order.objects.none()
        return Order.objects.all()  # 관리자: 모든 주문 조회

    @action(detail=False, methods=["get"], url_path="stats/completed")
    def completed_orders_stats(self, request):
        """배송 완료 주문 총 매출"""
        total_sales = (
            OrderItem.objects.filter(order__status="배송완료").aggregate(total=Sum("total_price"))["total"] or 0
        )
        return Response({"total_sales": total_sales})
