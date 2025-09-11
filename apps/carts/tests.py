from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from products.models import Product
from .models import Cart

User = get_user_model()


class CartAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@test.com", password="password123")
        self.client.login(email="test@test.com", password="password123")
        self.product = Product.objects.create(name="테스트 상품", price=10000)

    def test_add_to_cart(self):
        url = reverse("cart-list-create")
        data = {"product": self.product.id, "quantity": 2}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cart.objects.count(), 1)

    def test_view_cart(self):
        Cart.objects.create(user=self.user, product=self.product, quantity=1)
        url = reverse("cart-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
