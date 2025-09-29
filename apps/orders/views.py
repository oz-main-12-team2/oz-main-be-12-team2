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
        # n+1 문제 방지
        return Order.objects.filter(user=self.request.user).prefetch_related("items__product").order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            cart = get_object_or_404(
                Cart.objects.select_for_update().prefetch_related("items__product"), user=request.user
            )

            selected_items = serializer.validated_data.get("selected_items")
            if not selected_items:
                return Response({"detail": "No items selected for order"}, status=status.HTTP_400_BAD_REQUEST)

            cart_items = cart.items.filter(product__id__in=selected_items).select_related("product")
            if not cart_items.exists():
                return Response({"detail": "No valid items in cart"}, status=status.HTTP_400_BAD_REQUEST)

            order = Order.objects.create(
                user=request.user,
                recipient_name=serializer.validated_data["recipient_name"],
                recipient_phone=serializer.validated_data["recipient_phone"],
                recipient_address=serializer.validated_data["recipient_address"],
                total_price=Decimal("0.00"),
            )

            order_items = []
            total_price = Decimal("0.00")
            for item in cart_items:
                line_total = (item.product.price * item.quantity).quantize(Decimal("0.01"))
                total_price += line_total
                order_items.append(
                    OrderItem(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        unit_price=item.product.price,
                        total_price=line_total,
                    )
                )

            OrderItem.objects.bulk_create(order_items)
            order.total_price = total_price
            order.save()

            cart_items.delete()

        read_serializer = OrderSerializer(order)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)
