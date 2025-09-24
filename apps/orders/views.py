from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..carts.models import Cart
from .models import Order, OrderItem
from .serializers import OrderCreateSerializer, OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put", "delete"]

    def get_queryset(self):
        # 로그인한 사용자의 주문만 조회
        return Order.objects.filter(user=self.request.user).order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            # 장바구니 조회 및 잠금
            cart = get_object_or_404(
                Cart.objects.select_for_update().prefetch_related("items__product"), user=request.user
            )

            # 장바구니가 비어있으면 주문 불가
            if not cart.items.exists():
                return Response({"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

            # 선택된 상품 ID 가져오기
            selected_items = serializer.validated_data.get("selected_items")

            # 선택 항목 없으면 주문 불가
            if not selected_items:
                return Response({"detail": "No items selected for order"}, status=status.HTTP_400_BAD_REQUEST)

            # 선택된 CartProduct만 주문 처리
            cart_items = cart.items.filter(product__id__in=selected_items).select_related("product")

            if not cart_items.exists():
                return Response({"detail": "No valid items in cart"}, status=status.HTTP_400_BAD_REQUEST)

            # 수령인 정보
            recipient_name = serializer.validated_data.get("recipient_name")
            recipient_phone = serializer.validated_data.get("recipient_phone")
            recipient_address = serializer.validated_data.get("recipient_address")

            # 주문 생성
            order = Order.objects.create(
                user=request.user,
                recipient_name=recipient_name,
                recipient_phone=recipient_phone,
                recipient_address=recipient_address,
                total_price=Decimal("0.00"),
            )

            # 주문 아이템 생성 및 총액 계산
            total_price = Decimal("0.00")
            order_items = []
            for item in cart_items:
                unit_price = item.product.price
                quantity = item.quantity
                line_total = (unit_price * quantity).quantize(Decimal("0.01"))
                total_price += line_total

                order_items.append(
                    OrderItem(
                        order=order,
                        product=item.product,
                        quantity=quantity,
                        unit_price=unit_price,
                        total_price=line_total,
                    )
                )

            OrderItem.objects.bulk_create(order_items)

            # 주문 총액 업데이트
            order.total_price = total_price
            order.save()

            # 장바구니에서 주문한 아이템 삭제
            cart_items.delete()

        # 응답
        read_serializer = OrderSerializer(order)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)
