from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """
    Product 모델을 위한 시리얼라이저입니다.
    """

    class Meta:
        model = Product
        # 모든 필드를 시리얼라이즈합니다.
        fields = "__all__"

        # 특정 필드만 포함하거나 제외할 수도 있습니다.
        # fields = ['id', 'name', 'description', 'author', 'price', 'stock', 'category', 'image_url']
        # exclude = ['created_at', 'updated_at']
