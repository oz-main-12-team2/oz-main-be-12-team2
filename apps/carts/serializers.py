from rest_framework import serializers

from ..products.models import Product
from .models import Cart, CartProduct


class CartProductSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(source="product", queryset=Product.objects.all())
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_price = serializers.DecimalField(source="product.price", max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartProduct
        fields = ["product_id", "product_name", "product_price", "quantity"]

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("수량은 최소 1 이상이어야 합니다.")
        return value


class CartProductDetailSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(source="product", read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)
    product_price = serializers.DecimalField(source="product.price", max_digits=10, decimal_places=2, read_only=True)
    product_category = serializers.CharField(source="product.category.name", read_only=True)
    product_publisher = serializers.CharField(source="product.publisher", read_only=True)
    product_author = serializers.CharField(source="product.author", read_only=True)
    product_stock = serializers.IntegerField(source="product.stock", read_only=True)
    product_image = serializers.ImageField(source="product.image", read_only=True)

    class Meta:
        model = CartProduct
        fields = [
            "product_id",
            "product_name",
            "product_price",
            "product_category",
            "product_publisher",
            "product_author",
            "product_stock",
            "product_image",
            "quantity",
        ]


class CartSerializer(serializers.ModelSerializer):
    items = CartProductDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["items"]


class CartProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartProduct
        fields = ["quantity"]  # ✅ 수량만 업데이트 허용
