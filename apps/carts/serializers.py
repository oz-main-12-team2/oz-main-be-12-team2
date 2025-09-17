from rest_framework import serializers

from .models import Cart, CartProduct


class CartProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_price = serializers.DecimalField(
        source="product.price", max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = CartProduct
        fields = ["id", "product_name", "product_price", "quantity"]

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("수량은 최소 1 이상이어야 합니다.")
        return value


class CartSerializer(serializers.ModelSerializer):
    items = CartProductSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["items"]
        # read_only_fields = ["user", "id", "created_at", "updated_at"]
