# admin_views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from ..orders.models import Order
from ..orders.serializers import OrderSerializer


class AdminOrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]

    http_method_names = ["get", "post", "put", "delete"]  # PATCH 제거

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Order.objects.none()
        # 관리자: 모든 주문 조회, 생성일 기준 내림차순 정렬
        return Order.objects.all().order_by("-created_at")
