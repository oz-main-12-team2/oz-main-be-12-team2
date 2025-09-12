from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Cart, CartItem, Order
from .serializers import CartItemSerializer, CartSerializer, OrderSerializer


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def add_item(self, request, product_id, quantity):
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
        return Order.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user)
        if not cart.cartitem_set.exists():
            return Response({'detail': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        total_price = sum([item.product.price * item.quantity for item in cart.cartitem_set.all()])
        order = Order.objects.create(user=request.user, total_price=total_price)

        for item in cart.cartitem_set.all():
            order.items.create(product=item.product, quantity=item.quantity, price=item.product.price)
        cart.cartitem_set.all().delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data)
