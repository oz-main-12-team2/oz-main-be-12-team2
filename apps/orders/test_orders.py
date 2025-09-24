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
    """주문 API 테스트"""

    @classmethod
    def setUpTestData(cls):
        # 유저 / 관리자 생성
        cls.user = User.objects.create_user(
            email="testuser@example.com", name="테스트 유저", password="testpass"
        )
        cls.user.is_active = True
        cls.user.save()

        cls.admin_user = User.objects.create_superuser(
            email="admin@example.com", name="관리자", password="adminpass"
        )
        cls.admin_user.is_active = True
        cls.admin_user.save()

        # ✅ 유저 생성 시 자동 생성된 카트 가져오기
        cls.cart = cls.user.cart

        # 상품 생성
        cls.product = Product.objects.create(
            name="테스트 상품",
            description="테스트 설명",
            author="테스트 작가",
            publisher="테스트 출판사",
            price=Decimal("10000.00"),
            stock=10,
            category="소설",
            image_url="http://example.com/image.jpg",
        )

        # 기본 주문 생성
        cls.order = Order.objects.create(
            user=cls.user,
            recipient_name="홍길동",
            recipient_phone="010-1234-5678",
            recipient_address="서울시 강남구",
            total_price=Decimal("20000.00"),
            status="결제 완료",
        )

    def setUp(self):
        """각 테스트 실행 전 클라이언트 인증 및 CartProduct 보장"""
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # 테스트 DB에서 CartProduct가 항상 존재하도록 보장
        if not self.cart.items.exists():
            self.cart_item = CartProduct.objects.create(
                cart=self.cart,
                product=self.product,
                quantity=2
            )
        else:
            self.cart_item = self.cart.items.first()

    def create_order_payload(self, **kwargs):
        """
        주문 생성 시 payload
        - selected_items: 단순 정수 ID 리스트
        """
        payload = {
            "recipient_name": "홍길동",
            "recipient_phone": "010-1234-5678",
            "recipient_address": "서울시 강남구",
            "selected_items": [self.cart_item.id],  # 단순 ID 리스트
        }
        payload.update(kwargs)
        return payload

    def get_order_url(self, pk=None):
        if pk:
            return reverse("orders:order-detail", kwargs={"pk": pk})
        return reverse("orders:order-list")

    # === CRUD 테스트 ===
    def test_list_orders(self):
        response = self.client.get(self.get_order_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)

    def test_create_order(self):
        payload = self.create_order_payload()
        response = self.client.post(self.get_order_url(), payload, format="json")
        if response.status_code != status.HTTP_201_CREATED:
            print(response.data)  # 실패 시 에러 확인
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertGreaterEqual(Order.objects.count(), 2)

    def test_retrieve_order(self):
        response = self.client.get(self.get_order_url(self.order.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["order_number"], self.order.order_number)

    def test_update_order(self):
        payload = self.create_order_payload(
            recipient_name="김철수",
            recipient_phone="010-1111-2222",
            recipient_address="서울시 마포구",
        )
        response = self.client.put(self.get_order_url(self.order.id), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.recipient_name, "김철수")

    def test_delete_order(self):
        response = self.client.delete(self.get_order_url(self.order.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())

    # === 상태 변경 테스트 (PUT) ===
    def test_update_order_status_success(self):
        payload = self.create_order_payload(status="배송중")
        response = self.client.put(self.get_order_url(self.order.id), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "배송중")

    # === Admin & User 테스트 ===
    def test_list_my_orders(self):
        response = self.client.get(self.get_order_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_list_orders(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.get_order_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
