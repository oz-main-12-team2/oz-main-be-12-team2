from django.db.models import Sum
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view

from apps.orders.models import OrderItem  # OrderDetail 모델이 필요합니다.

from .models import Product


# 책 목록을 보여주는 뷰 (랭킹 정보 추가)
@api_view(["GET"])
def product_list(request):
    """
    책 목록과 함께 랭킹을 메인 페이지에 보여주는 뷰
    """
    # 1. 전체 상품 목록 가져오기
    products = Product.objects.all()

    # 2. 판매량 순으로 상위 3개 랭킹 상품 가져오기
    # OrderDetail 모델이 Order 모델을 통해 '배송완료' 상태를 필터링
    top_ranking_products = (
        OrderItem.objects.filter(order__status="배송완료")
        .values("product_id", "product__name")
        .annotate(order_count=Sum("quantity"))
        .order_by("-order_count")[:3]
    )

    # 3. 두 데이터를 하나의 컨텍스트 딕셔너리에 담아 템플릿에 전달
    context = {
        "products": products,
        "top_ranking_products": top_ranking_products,
    }

    return render(request, "products/product_list.html", context)


# 책 상세 정보를 보여주는 뷰
@api_view(["GET"])
def product_detail(request, pk):
    """
    책 상세 정보를 보여주는 뷰
    """
    product = get_object_or_404(Product, pk=pk)
    return render(request, "products/product_detail.html", {"product": product})


# 기타 일반 사용자용 뷰 (예: 검색, 리뷰 등)를 추가
