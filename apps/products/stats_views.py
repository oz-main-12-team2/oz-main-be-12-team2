# /apps/products/stats_views.py (최종 수정본)

from datetime import timedelta

# ExpressionWrapper를 새로 import 합니다.
from django.db.models import DecimalField, ExpressionWrapper, F, Sum, Value
from django.db.models.functions import Coalesce
from django.http import HttpResponseForbidden, JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET

from apps.orders.models import OrderItem
from apps.products.models import Product


@require_GET
def admin_sales_stats(request):
    # --- 이 부분을 추가하여 뷰를 더 안전하게 만듭니다 --- #
    # --- 디버깅 코드 추가 ---
    print(f"[VIEW] request.user: {request.user}")
    print(f"[VIEW] request.user.is_authenticated: {request.user.is_authenticated}")
    print(f"[VIEW] request.user.is_admin: {request.user.is_admin}")
    # -----------------------

    # 1. 사용자가 로그인했는지 먼저 확인
    if not request.user.is_authenticated:
        return HttpResponseForbidden("로그인이 필요합니다.")

    # 2. 로그인했다면, 관리자인지 확인
    if not request.user.is_admin:
        return HttpResponseForbidden("관리자만 접근 가능합니다.")
    # -------------------------------------------------- #

    """
    관리자 대시보드에 필요한 상품 및 판매 통계를 JSON으로 반환합니다.
    """
    # ... (이하 로직은 그대로) ...
    # --- 1. 재고 상태 계산 ---
    # ExpressionWrapper를 사용하여 계산 타입을 명확히 지정
    total_stock_value = Product.objects.aggregate(
        total_value=Coalesce(
            Sum(ExpressionWrapper(F("price") * F("stock"), output_field=DecimalField())),
            Value(0, output_field=DecimalField()),
        )
    )["total_value"]

    # 판매 중인 상품 개수 (재고가 1개 이상인 상품)
    products_on_sale_count = Product.objects.filter(stock__gt=0).count()

    # --- 2. 기간별 판매 통계 계산 ---
    today = timezone.now().date()
    start_of_this_month = today.replace(day=1)
    completed_orders = OrderItem.objects.filter(order__status="배송완료")
    sales_today = completed_orders.filter(order__created_at__date=today).aggregate(total=Coalesce(Sum("quantity"), 0))[
        "total"
    ]
    thirty_days_ago = today - timedelta(days=30)
    sales_last_30_days = completed_orders.filter(order__created_at__date__gte=thirty_days_ago).aggregate(
        total=Coalesce(Sum("quantity"), 0)
    )["total"]
    sales_this_month = completed_orders.filter(order__created_at__date__gte=start_of_this_month).aggregate(
        total=Coalesce(Sum("quantity"), 0)
    )["total"]

    # --- 3. JSON 데이터 구성 ---
    data = {
        "stock_status": {
            "total_stock_value": total_stock_value,
            "on_sale_count": products_on_sale_count,
        },
        "sales_statistics": {
            "today": sales_today,
            "last_30_days": sales_last_30_days,
            "this_month": sales_this_month,
        },
    }

    return JsonResponse(data)
