# apps/stats/services.py
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.db.models.functions import TruncDate

from apps.orders.models import Order, OrderItem
from apps.products.models import Product

User = get_user_model()


def get_total_users():
    return User.objects.count()


def get_total_revenue():
    return OrderItem.objects.aggregate(total=Sum("total_price"))["total"] or 0


def get_total_stock():
    return Product.objects.aggregate(total=Sum("stock"))["total"] or 0


def get_today_orders(base_date):
    return Order.objects.filter(created_at__date=base_date).count()


def get_daily_sales(base_date):
    qs = OrderItem.objects.filter(order__created_at__date=base_date)
    result = qs.aggregate(quantity=Sum("quantity"), revenue=Sum("total_price"))
    return {
        "quantity": result["quantity"] or 0,
        "revenue": result["revenue"] or 0,
    }


def get_weekly_sales(base_date):
    week_start = base_date - timedelta(days=base_date.weekday())
    week_end = week_start + timedelta(days=6)
    qs = OrderItem.objects.filter(order__created_at__date__range=[week_start, week_end])
    result = qs.aggregate(quantity=Sum("quantity"), revenue=Sum("total_price"))
    return {
        "quantity": result["quantity"] or 0,
        "revenue": result["revenue"] or 0,
    }


def get_monthly_sales(base_date):
    qs = OrderItem.objects.filter(
        order__created_at__year=base_date.year,
        order__created_at__month=base_date.month,
    )
    result = qs.aggregate(quantity=Sum("quantity"), revenue=Sum("total_price"))
    return {
        "quantity": result["quantity"] or 0,
        "revenue": result["revenue"] or 0,
    }


def get_trend(base_date, days=30):
    """
    최근 N일간 추세 (단일 쿼리 + 빠진 날짜는 0으로 채우기)
    """
    trend_qs = (
        OrderItem.objects.filter(order__created_at__date__gte=base_date - timedelta(days=days - 1))
        .annotate(date=TruncDate("order__created_at"))
        .values("date")
        .annotate(quantity=Sum("quantity"), revenue=Sum("total_price"))
        .order_by("date")
    )

    trend_map = {t["date"]: t for t in trend_qs}

    result = []
    for i in range(days):
        d = base_date - timedelta(days=days - 1 - i)  # 과거 → 오늘 순서
        record = trend_map.get(d, {"quantity": 0, "revenue": 0})
        result.append(
            {
                "date": d,
                "quantity": record["quantity"] or 0,
                "revenue": record["revenue"] or 0,
            }
        )

    return result


def get_dashboard_data(base_date):
    """
    대시보드 전체 통계 (ThreadPoolExecutor로 병렬 처리)
    """

    if getattr(settings, "TESTING", False):
        # 순차 실행 (테스트 환경)
        return {
            "total_users": get_total_users(),
            "total_revenue": get_total_revenue(),
            "total_stock": get_total_stock(),
            "today_orders": get_today_orders(base_date),
            "daily_sales": get_daily_sales(base_date),
            "weekly_sales": get_weekly_sales(base_date),
            "monthly_sales": get_monthly_sales(base_date),
            "trend": get_trend(base_date),
        }

    with ThreadPoolExecutor() as executor:
        futures = {
            "total_users": executor.submit(get_total_users),
            "total_revenue": executor.submit(get_total_revenue),
            "total_stock": executor.submit(get_total_stock),
            "today_orders": executor.submit(get_today_orders, base_date),
            "daily_sales": executor.submit(get_daily_sales, base_date),
            "weekly_sales": executor.submit(get_weekly_sales, base_date),
            "monthly_sales": executor.submit(get_monthly_sales, base_date),
            "trend": executor.submit(get_trend, base_date),
        }
        return {key: f.result() for key, f in futures.items()}
