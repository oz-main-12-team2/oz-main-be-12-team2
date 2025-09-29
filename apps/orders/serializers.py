from rest_framework import serializers

from apps.products.serializers import ProductSerializer

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "unit_price", "total_price"]
        read_only_fields = ["total_price"]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("수량은 1 이상이어야 합니다.")
        return value

    def validate_unit_price(self, value):
        if value < 0:
            raise serializers.ValidationError("상품 가격은 0 이상이어야 합니다.")
        return value


class OrderCreateSerializer(serializers.ModelSerializer):
    selected_items = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        help_text="장바구니에서 선택한 아이템 ID 리스트",
    )

    class Meta:
        model = Order
        fields = ["recipient_name", "recipient_phone", "recipient_address", "selected_items"]

    def validate_recipient_phone(self, value):
        import re

        if not re.match(r"^01[016789]-\d{3,4}-\d{4}$", value):
            raise serializers.ValidationError("전화번호 형식이 올바르지 않습니다.")
        return value

    def validate_recipient_name(self, value):
        if not (2 <= len(value) <= 10):
            raise serializers.ValidationError("이름은 2~10자여야 합니다.")
        return value


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
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
