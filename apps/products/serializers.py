from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """
    Product 모델을 위한 시리얼라이저입니다.
    """

    class Meta:
        model = Product
        fields = "__all__"


# 상품 통계 serializer
class SalesTrendSerializer(serializers.Serializer):
    date = serializers.DateField()
    quantity = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=15, decimal_places=2)


class ProductSalesStatisticsSerializer(serializers.Serializer):
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    today = serializers.DictField(child=serializers.IntegerField(), allow_null=True)
    week = serializers.DictField(child=serializers.IntegerField(), allow_null=True)
    month = serializers.DictField(child=serializers.IntegerField(), allow_null=True)
    trend = SalesTrendSerializer(many=True)
