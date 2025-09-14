import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.orders.models import Order
from apps.payments.models import Payment, PaymentMethod, PaymentStatus

User = get_user_model()


@pytest.mark.django_db
class TestUserPaymentAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="user@test.com", password="password123")
        self.order = Order.objects.create(user=self.user, total_price=10000)

    def test_create_payment_success(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/payment/create/",
            {
                "order_id": self.order.id,
                "method": PaymentMethod.CARD,
                "total_price": "45000.00",
                "status": PaymentStatus.SUCCESS,
            },
            format="json",
        )

        assert response.status_code == 201
        assert response.data["success"] is True
        assert response.data["data"]["method"] == PaymentMethod.CARD
        assert Payment.objects.count() == 1

    def test_create_payment_other_user_order(self):
        other_user = User.objects.create_user(email="other@test.com", password="password123")
        other_order = Order.objects.create(user=other_user, total_price=20000)

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/payment/create/",
            {
                "order_id": other_order.id,
                "method": PaymentMethod.CARD,
                "total_price": "20000.00",
                "status": PaymentStatus.SUCCESS,
            },
            format="json",
        )

        # 본인 주문이 아니므로 생성 불가
        assert response.status_code == 400 or response.status_code == 403

    def test_user_can_list_own_payments(self):
        Payment.objects.create(
            order=self.order, method=PaymentMethod.CARD, total_price=10000, status=PaymentStatus.SUCCESS
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/payment/")

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["order_id"] == self.order.id

    def test_user_can_retrieve_own_payment(self):
        payment = Payment.objects.create(
            order=self.order, method=PaymentMethod.CARD, total_price=10000, status=PaymentStatus.SUCCESS
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/payment/{payment.id}/")

        assert response.status_code == 200
        assert response.data["id"] == payment.id

    def test_user_cannot_access_others_payment(self):
        other_user = User.objects.create_user(email="other@test.com", password="password123")
        other_order = Order.objects.create(user=other_user, total_price=20000)
        other_payment = Payment.objects.create(
            order=other_order, method=PaymentMethod.CARD, total_price=20000, status=PaymentStatus.SUCCESS
        )

        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/api/payment/{other_payment.id}/")

        assert response.status_code == 404  # 접근 불가


@pytest.mark.django_db
class TestAdminPaymentAPI:
    def setup_method(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(email="admin@test.com", password="admin123")
        self.user = User.objects.create_user(email="user@test.com", password="password123")
        self.order = Order.objects.create(user=self.user, total_price=10000)
        self.payment = Payment.objects.create(
            order=self.order,
            method=PaymentMethod.CARD,
            total_price=10000,
            status=PaymentStatus.SUCCESS,
        )

    def test_admin_can_list_all_payments(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/admin/payment/")

        assert response.status_code == 200
        assert len(response.data) >= 1

    def test_admin_can_retrieve_payment(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f"/api/admin/payment/{self.payment.id}/")

        assert response.status_code == 200
        assert response.data["id"] == self.payment.id

    def test_non_admin_cannot_access_admin_endpoints(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/api/admin/payment/")

        assert response.status_code == 403
