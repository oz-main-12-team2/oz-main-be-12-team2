from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.carts.models import Cart, CartProduct
from apps.products.models import Product
from apps.users.models import User


class CartAPITest(TestCase):
    """장바구니 API 테스트"""

    @classmethod
    def setUpTestData(cls):
        """테스트에 필요한 공통 데이터는 한 번만 생성"""
        cls.user = User.objects.create_user(email="test@example.com", name="테스트 사용자", password="testpass123")
        cls.product = Product.objects.create(
            name="테스트 상품",
            description="테스트 설명",
            author="테스트 작가",
            publisher="테스트 출판사",
            price=Decimal("10000.00"),  # ✅ Decimal로 저장
            stock=10,
            category="소설",
            image_url="http://example.com/image.jpg",
        )

    def setUp(self):
        """각 테스트마다 인증 클라이언트만 준비"""
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_cart_list(self):
        """장바구니 조회"""
        url = reverse("cart-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        # 최상위 구조 검증
        self.assertIsInstance(data, dict)
        self.assertIn("results", data)
        self.assertIsInstance(data["results"], list)

        # 결과값 세부 검증 - 길이로 체크
        self.assertEqual(data["count"], len(data["results"]))

    def test_add_product_to_cart(self):
        """장바구니에 상품 추가"""
        url = reverse("cart-add")
        data = {"product_id": self.product.id, "quantity": 2}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["quantity"], 2)
        self.assertEqual(response.data["product_id"], self.product.id)

    def test_update_cart_product_quantity(self):
        """상품 수량 변경"""
        cart, _ = Cart.objects.get_or_create(user=self.user)
        cart_product = CartProduct.objects.create(cart=cart, product=self.product, quantity=1)

        url = reverse("cart-update", args=[self.product.id])
        data = {"product_id": self.product.id, "quantity": 5}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["quantity"], 5)

    def test_delete_cart_product(self):
        """장바구니 상품 삭제"""
        cart, _ = Cart.objects.get_or_create(user=self.user)
        cart_product = CartProduct.objects.create(cart=cart, product=self.product, quantity=1)

        url = reverse("cart-update", args=[self.product.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CartProduct.objects.filter(id=cart_product.id).exists())

    def test_clear_cart(self):
        """장바구니 전체 비우기"""
        cart, _ = Cart.objects.get_or_create(user=self.user)
        CartProduct.objects.create(cart=cart, product=self.product, quantity=2)

        url = reverse("cart-clear")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(cart.items.count(), 0)
