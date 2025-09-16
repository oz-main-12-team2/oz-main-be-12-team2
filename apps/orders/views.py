from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..carts.models import Cart
from .models import Order, OrderItem
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    # PATCH 제거, DELETE도 필요 없으면 제거 가능
    http_method_names = ["get", "post", "put"]  # PATCH 제외, DELETE 제외

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Order.objects.none()
        if not self.request.user.is_authenticated:
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        # 사용자 장바구니 가져오기
        cart = get_object_or_404(Cart, user=request.user)

        if not hasattr(cart, "items") or not cart.items.exists():
            return Response({"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        recipient_name = request.data.get("recipient_name")
        recipient_phone = request.data.get("recipient_phone")
        recipient_address = request.data.get("recipient_address")

        order = Order.objects.create(
            user=request.user,
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            recipient_address=recipient_address,
            total_price=0,
        )

        total_price = 0
        for item in cart.items.all():
            order_item = OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.product.price,
            )
            total_price += order_item.total_price

        order.total_price = total_price
        order.save()

        cart.items.all().delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def completed_orders_stats(self, request):
        total_sales = (
            OrderItem.objects.filter(order__status="배송완료").aggregate(total=Sum("total_price"))["total"] or 0
        )
        return Response({"total_sales": total_sales})
