from rest_framework import serializers

from ..orders.models import Order
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    # 요청과 응답 모두 order_id를 사용
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(),
        source="order",  # 내부적으로 Payment.order(FK)와 연결
    )

    class Meta:
        model = Payment
        fields = ["id", "order_id", "method", "total_price", "status", "created_at"]
        read_only_fields = ["id", "created_at"]
