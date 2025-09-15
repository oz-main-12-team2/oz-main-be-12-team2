from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Payment
        fields = ["id", "order_id", "method", "total_price", "status", "created_at"]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        order_id = validated_data.pop("order_id")
        from apps.orders.models import Order  # 지연 import

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise serializers.ValidationError({"order_id": "해당 주문을 찾을 수 없습니다."})

        payment = Payment.objects.create(order=order, **validated_data)
        return payment
