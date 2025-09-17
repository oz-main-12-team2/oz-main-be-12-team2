from django.urls import path

from .views import CartClearView, CartListView, CartProductCreateView, CartProductUpdateDeleteView

urlpatterns = [
    path("", CartListView.as_view(), name="cart-list"),  # 장바구니 조회
    path("items/", CartProductCreateView.as_view(), name="cart-add"),  # 장바구니 상품 추가
    path("items/<int:pk>/", CartProductUpdateDeleteView.as_view(), name="cart-update"),  # 수량 변경
    path("clear/", CartClearView.as_view(), name="cart-clear"),  # ✅ 장바구니 전체 비우기
]
