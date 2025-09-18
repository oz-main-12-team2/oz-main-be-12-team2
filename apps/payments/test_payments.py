from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.orders.models import Order, OrderItem
from apps.payments.models import Payment, PaymentMethod, PaymentStatus
from apps.products.models import Product

User = get_user_model()


class BasePaymentTestCase(APITestCase):
    """공통 데이터와 헬퍼 메서드 정의"""

    @classmethod
    def setUpTestData(cls):
        # 관리자 / 일반 유저 생성
        cls.admin = User.objects.create_superuser(
            email="admin@test.com",
            password="admin123",
            name="관리자",
        )
        cls.user = User.objects.create_user(
            email="user@test.com",
            password="password123",
            name="테스트유저",
        )

        # 상품 생성
        cls.product = Product.objects.create(name="테스트상품", price=10000, stock=10)

    def create_order(self, user=None, total_price=10000):
        """주문 + 주문상품 생성 헬퍼"""
        if user is None:
            user = self.user

        order = Order.objects.create(
            user=user,
            total_price=total_price,
            recipient_name="홍길동",
            recipient_phone="010-1234-5678",
            recipient_address="서울시 테스트구 테스트동",
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
            unit_price=self.product.price,
            total_price=total_price,
        )
        return order


class UserPaymentAPITest(BasePaymentTestCase):
    def setUp(self):
        # 로그인 기본값 = 일반 사용자
        self.client.force_authenticate(user=self.user)
        # 기본 주문 생성
        self.order = self.create_order(user=self.user, total_price=10000)

    def test_create_payment_success(self):
        url = reverse("payment-create")
        response = self.client.post(
            url,
            {
                "order_id": self.order.id,
                "method": PaymentMethod.CARD,
                "total_price": "10000.00",
                "status": PaymentStatus.SUCCESS,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["method"], PaymentMethod.CARD)
        self.assertEqual(Payment.objects.count(), 1)

    def test_create_payment_other_user_order(self):
        other_user = User.objects.create_user(
            email="other@test.com",
            password="password123",
            name="다른유저",
        )
        other_order = self.create_order(user=other_user, total_price=20000)

        url = reverse("payment-create")
        response = self.client.post(
            url,
            {
                "order_id": other_order.id,
                "method": PaymentMethod.CARD,
                "total_price": "20000.00",
                "status": PaymentStatus.SUCCESS,
            },
            format="json",
        )

        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN])

    def test_user_can_list_own_payments(self):
        Payment.objects.create(
            order=self.order,
            method=PaymentMethod.CARD,
            total_price=10000,
            status=PaymentStatus.SUCCESS,
        )

        url = reverse("user-payment-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data.get("results", response.data)  # pagination 대응
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["order_id"], self.order.id)

    def test_user_can_retrieve_own_payment(self):
        payment = Payment.objects.create(
            order=self.order,
            method=PaymentMethod.CARD,
            total_price=10000,
            status=PaymentStatus.SUCCESS,
        )

        url = reverse("user-payment-detail", kwargs={"pk": payment.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], payment.id)

    def test_user_cannot_access_others_payment(self):
        other_user = User.objects.create_user(
            email="other@test.com",
            password="password123",
            name="다른유저",
        )
        other_order = self.create_order(user=other_user, total_price=20000)
        other_payment = Payment.objects.create(
            order=other_order,
            method=PaymentMethod.CARD,
            total_price=20000,
            status=PaymentStatus.SUCCESS,
        )

        url = reverse("user-payment-detail", kwargs={"pk": other_payment.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AdminPaymentAPITest(BasePaymentTestCase):
    def setUp(self):
        # 로그인 기본값 = 관리자
        self.client.force_authenticate(user=self.admin)
        self.order = self.create_order(user=self.user, total_price=15000)
        self.payment = Payment.objects.create(
            order=self.order,
            method=PaymentMethod.CARD,
            total_price=15000,
            status=PaymentStatus.SUCCESS,
        )

    def test_admin_can_list_all_payments(self):
        url = reverse("admin-payment-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_admin_can_retrieve_payment(self):
        url = reverse("admin-payment-detail", kwargs={"pk": self.payment.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.payment.id)

    def test_non_admin_cannot_access_admin_endpoints(self):
        self.client.force_authenticate(user=self.user)  # 일반 유저로 로그인
        url = reverse("admin-payment-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
