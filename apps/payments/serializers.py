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
        read_only_fields = ["id", "total_price", "created_at"]

    def create(self, validated_data):
        order = validated_data["order"]
        validated_data["total_price"] = order.total_price  # 생성 시 자동 세팅
        return super().create(validated_data)
