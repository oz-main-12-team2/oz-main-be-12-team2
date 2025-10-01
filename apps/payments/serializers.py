from rest_framework import serializers

from ..orders.models import Order
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """일반 사용자용 결제 직렬화기"""

    # 요청과 응답 모두 order_id를 사용
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.prefetch_related("payments"),
        source="order",  # 내부적으로 Payment.order(FK)와 연결
    )

    class Meta:
        model = Payment
        fields = ["id", "order_id", "method", "total_price", "status", "transaction_id", "created_at"]
        read_only_fields = ["id", "total_price", "status", "transaction_id", "created_at"]

    def create(self, validated_data):
        order = validated_data["order"]
        validated_data["total_price"] = order.total_price  # 생성 시 자동 세팅
        return super().create(validated_data)


class AdminPaymentSerializer(serializers.ModelSerializer):
    """관리자용 결제 직렬화기 (유저 정보 포함)"""

    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.prefetch_related("payments"),
        source="order",
    )
    user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "order_id",
            "method",
            "total_price",
            "status",
            "transaction_id",
            "created_at",
            "user",
        ]
        read_only_fields = ["id", "total_price", "status", "transaction_id", "created_at"]

    def get_user(self, obj):
        """주문과 연결된 유저 정보를 반환"""
        if obj.order and obj.order.user:
            return {
                "id": obj.order.user.id,
                "email": obj.order.user.email,
                "name": obj.order.user.name,
            }
        return None
