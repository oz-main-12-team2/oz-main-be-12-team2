from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.orders.models import Order

# Cart/CartItem 임포트 시 related_name 확인
try:
    from apps.carts.models import Cart, CartItem
except ImportError:
    Cart = None
    CartItem = None

User = get_user_model()


class OrdersAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="testuser@example.com", name="테스트 유저", password="testpass")
        self.admin_user = User.objects.create_superuser(email="admin@example.com", name="관리자", password="adminpass")
        self.client.force_authenticate(user=self.user)

        # Cart 및 CartItem 생성 (related_name="items" 기준)
        if Cart and CartItem:
            self.cart = Cart.objects.create(user=self.user)
            CartItem.objects.create(cart=self.cart, product_name="상품1", quantity=1, price=10000)
        else:
            self.cart = None

        # 기본 주문
        self.order = Order.objects.create(
            user=self.user,
            recipient_name="홍길동",
            recipient_phone="010-1234-5678",
            recipient_address="서울시 강남구",
            total_price=45000,
            status="결제 완료",
        )

    def create_order_payload(self, **kwargs):
        payload = {
            "recipient_name": "홍길동",
            "recipient_phone": "010-1234-5678",
            "recipient_address": "서울시 강남구",
            "status": "결제 완료",
        }
        # total_price는 serializer에서 자동 계산하므로 제거
        if self.cart:
            payload["cart"] = self.cart.id
        payload.update(kwargs)
        return payload

    def get_order_url(self, pk=None):
        """
        네임스페이스 포함 URL reverse
        """
        if pk:
            return reverse("orders:order-detail", kwargs={"pk": pk})
        return reverse("orders:order-list")

    # CRUD 테스트
    def test_list_orders(self):
        response = self.client.get(self.get_order_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)

    def test_create_order(self):
        if not self.cart:
            self.skipTest("Cart or CartItem 모델 없음")
        response = self.client.post(self.get_order_url(), self.create_order_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)

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

    def test_partial_update_order(self):
        response = self.client.patch(self.get_order_url(self.order.id), {"status": "배송중"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "배송중")

    def test_delete_order(self):
        response = self.client.delete(self.get_order_url(self.order.id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.count(), 0)

    # 상태 테스트
    def test_update_order_status_success(self):
        response = self.client.patch(self.get_order_url(self.order.id), {"status": "배송중"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "배송중")

    def test_update_order_status_invalid_value(self):
        response = self.client.patch(self.get_order_url(self.order.id), {"status": "잘못된상태"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_status_not_found(self):
        response = self.client.patch(self.get_order_url(9999), {"status": "배송중"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_order_status_unauthorized(self):
        self.client.force_authenticate(user=None)
        response = self.client.patch(self.get_order_url(self.order.id), {"status": "배송중"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Admin & User 테스트
    def test_list_my_orders(self):
        response = self.client.get(self.get_order_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_list_orders(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.get_order_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
