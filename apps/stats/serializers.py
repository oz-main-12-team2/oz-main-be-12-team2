from rest_framework import serializers


class SalesSummarySerializer(serializers.Serializer):
    quantity = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2)


class TrendSerializer(serializers.Serializer):
    date = serializers.DateField()
    quantity = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2)


class DashboardSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_stock = serializers.IntegerField()
    today_orders = serializers.IntegerField()

    daily_sales = SalesSummarySerializer()
    weekly_sales = SalesSummarySerializer()
    monthly_sales = SalesSummarySerializer()

    trend = TrendSerializer(many=True)  # ✅ DictField 대신 전용 Serializer


class ProductRankingSerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    product_id = serializers.IntegerField()
    name = serializers.CharField()
    quantity = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2)


class ProductRankingResponseSerializer(serializers.Serializer):
    period = serializers.CharField()
    rankings = ProductRankingSerializer(many=True)
