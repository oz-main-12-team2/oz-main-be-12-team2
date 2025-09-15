from rest_framework import serializers
from apps.products.serializers import ProductSerializer
from .models import Cart, CartItem, Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "user", "recipient_name", "recipient_phone",
                  "recipient_address", "total_price", "status",
                  "created_at", "updated_at", "items"]

    def get_total_price(self, obj):
        return sum(item.price * item.quantity for item in obj.items.all())


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source="cartitem_set", many=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "items"]
