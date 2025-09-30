from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.carts.models import CartProduct
from apps.orders.models import Order
from apps.products.models import Product

User = get_user_model()


class OrdersAPITestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # 사용자 생성
        cls.user = User.objects.create_user(email="testuser@example.com", name="테스트 유저", password="testpass")
        cls.user.is_active = True
        cls.user.save()

        # 장바구니 가져오기
        cls.cart = cls.user.cart

        # 상품 생성
        cls.product = Product.objects.create(
            name="테스트 상품",
            description="설명",
            author="작가",
            publisher="출판사",
            price=Decimal("10000.00"),
            stock=10,
            category="소설",
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        if not self.cart.items.exists():
            self.cart_item = CartProduct.objects.create(cart=self.cart, product=self.product, quantity=2)
        else:
            self.cart_item = self.cart.items.first()

    def get_order_url(self, pk=None):
        if pk:
            return reverse("orders:order-detail", kwargs={"pk": pk})
        return reverse("orders:order-list")

    def test_create_order_and_validate_total_price(self):
        payload = {
            "recipient_name": "홍길동",
            "recipient_phone": "010-1234-5678",
            "recipient_address": "서울시 강남구",
            "selected_items": [self.cart_item.product.id],
        }
        response = self.client.post(self.get_order_url(), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        order = Order.objects.get(order_number=response.data["order_number"])
        self.assertEqual(order.total_price, self.cart_item.product.price * self.cart_item.quantity)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().total_price, order.total_price)
