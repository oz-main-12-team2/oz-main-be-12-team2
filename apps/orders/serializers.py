from decimal import Decimal

from rest_framework import serializers

from apps.products.serializers import ProductSerializer

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "quantity",
            "unit_price",
            "total_price",
        ]
        read_only_fields = ["total_price"]  # total_price는 계산된 값만 표시


# 주문 생성용 serializer (Swagger 입력용)
class OrderCreateSerializer(serializers.ModelSerializer):
    selected_items = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="장바구니에서 선택한 아이템 ID 리스트",
    )

    class Meta:
        model = Order
        fields = [
            "recipient_name",
            "recipient_phone",
            "recipient_address",
            "selected_items",
        ]


# 조회/수정용 serializer
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )  # 수정: IntegerField → DecimalField
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "user",
            "recipient_name",
            "recipient_phone",
            "recipient_address",
            "total_price",
            "status",
            "created_at",
            "updated_at",
            "items",
        ]
        read_only_fields = ["total_price", "order_number"]
