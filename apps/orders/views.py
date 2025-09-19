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
        return Order.objects.filter(user=self.request.user).order_by("-created_at")

    # 액션에 따라 serializer 선택
    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = get_object_or_404(Cart, user=request.user)

        if not cart.items.exists():
            return Response({"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        selected_items = serializer.validated_data.get("selected_items")
        if selected_items:
            cart_items = cart.items.filter(id__in=selected_items)
        else:
            cart_items = cart.items.all()

        if not cart_items.exists():
            return Response({"detail": "No valid items in cart"}, status=status.HTTP_400_BAD_REQUEST)

        recipient_name = serializer.validated_data.get("recipient_name")
        recipient_phone = serializer.validated_data.get("recipient_phone")
        recipient_address = serializer.validated_data.get("recipient_address")

        order = Order.objects.create(
            user=request.user,
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            recipient_address=recipient_address,
            total_price=0,
        )

        total_price = 0
        for item in cart_items:
            order_item = OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.product.price,
            )
            total_price += order_item.total_price

        order.total_price = total_price
        order.save()

        cart_items.delete()

        read_serializer = OrderSerializer(order)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def my_order_detail(self, request, pk=None):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
