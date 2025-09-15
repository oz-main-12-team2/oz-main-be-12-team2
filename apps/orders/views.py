from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer, OrderSerializer


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Cart.objects.none()
        if not self.request.user.is_authenticated:
            return Cart.objects.none()
        return Cart.objects.filter(user=self.request.user)

    def add_item(self, request, product_id, quantity):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, product_id=product_id)
        item.quantity = quantity
        item.save()
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Order.objects.none()
        if not self.request.user.is_authenticated:
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        cart = get_object_or_404(Cart, user=request.user)
        if not cart.cartitem_set.exists():
            return Response({"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        recipient_name = request.data.get("recipient_name")
        recipient_phone = request.data.get("recipient_phone")
        recipient_address = request.data.get("recipient_address")

        order = Order.objects.create(
            user=request.user,
            recipient_name=recipient_name,
            recipient_phone=recipient_phone,
            recipient_address=recipient_address
        )

        for item in cart.cartitem_set.all():
            OrderItem.objects.create(
                order=order, product=item.product,
                quantity=item.quantity, price=item.product.price
            )
        cart.cartitem_set.all().delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def completed_orders_stats(self, request):
        total_sales = OrderItem.objects.filter(order__status="COMPLETED").aggregate(
            total=Sum("price")
        )["total"] or 0
        return Response({"total_sales": total_sales})
