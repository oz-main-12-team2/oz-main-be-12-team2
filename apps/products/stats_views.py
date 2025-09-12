from datetime import date, timedelta

from django.db.models import Sum
from django.http import JsonResponse

from .models import Product
from apps.orders.models import OrderItem


# 판매 통계 API
def admin_sales_stats(request):
    # 실제 구현 시, Order, OrderItem 모델 등을 사용하여 DB 쿼리 필요
    # 현재는 요청받은 명세서에 맞춰 더미 데이터를 반환
    today = date.today()

    # 더미 데이터
    total_revenue = 123456789.00
    today_stats = {"quantity": 120, "revenue": 350000}
    week_stats = {"quantity": 950, "revenue": 2780000}
    month_stats = {"quantity": 4200, "revenue": 12500000}

    trend = []
    for i in range(30):
        day = today - timedelta(days=i)
        trend.append(
            {
                "date": day.isoformat(),
                "quantity": 100 + i,  # 더미 데이터
                "revenue": 300000 + i * 1000,  # 더미 데이터
            }
        )

    data = {
        "total_revenue": total_revenue,
        "today": today_stats,
        "week": week_stats,
        "month": month_stats,
        "trend": trend,
    }

    return JsonResponse({"success": True, "data": data}, status=200)
