from datetime import datetime

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.orders.models import Order, OrderItem
from apps.products.models import Product
from apps.users.models import User


class BaseStatsTestCase(TestCase):
    """공통 테스트 데이터 생성"""

    @classmethod
    def setUpTestData(cls):
        # 관리자 유저
        cls.admin = User.objects.create_superuser(email="admin@test.com", password="admin123", name="admin")

        # 일반 유저
        cls.user1 = User.objects.create_user(email="user1@test.com", password="test123", name="user1")
        cls.user2 = User.objects.create_user(email="user2@test.com", password="test123", name="user2")

        # 상품
        cls.p1 = Product.objects.create(name="책1", stock=5, price=10000)
        cls.p2 = Product.objects.create(name="책2", stock=10, price=20000)

        # 주문 + 주문아이템
        cls.order = Order.objects.create(
            user=cls.admin,
            total_price=40000,  # 주문 총액 (아이템 합계와 맞게 지정)
            recipient_name="홍길동",
            recipient_phone="010-1111-2222",
            recipient_address="서울시 테스트구",
            created_at=datetime.today(),
        )
        OrderItem.objects.create(
            order=cls.order,
            product=cls.p1,
            quantity=2,
            unit_price=cls.p1.price,
            total_price=20000,
        )
        OrderItem.objects.create(
            order=cls.order,
            product=cls.p2,
            quantity=1,
            unit_price=cls.p2.price,
            total_price=20000,
        )

    def setUp(self):
        """각 테스트 실행 전에 client를 superuser로 인증"""
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)


class DashboardAPITest(BaseStatsTestCase):
    def test_dashboard_counts_and_sales(self):
        url = reverse("admin-dashboard")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["total_users"], 3)  # admin + 2명
        self.assertEqual(data["total_stock"], 15)
        self.assertEqual(data["today_orders"], 1)
        self.assertEqual(data["daily_sales"]["quantity"], 3)
        self.assertEqual(data["daily_sales"]["revenue"], "40000.00")


class ProductRankingAPITest(BaseStatsTestCase):
    def test_product_ranking(self):
        url = reverse("product-ranking")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        rankings = response.json()["rankings"]

        self.assertEqual(len(rankings), 2)
        self.assertEqual(rankings[0]["name"], "책1")
        self.assertEqual(rankings[0]["quantity"], 2)
        self.assertEqual(rankings[0]["rank"], 1)

    def test_product_ranking_empty(self):
        # 데이터 전부 삭제 후 확인
        OrderItem.objects.all().delete()

        url = reverse("product-ranking")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        rankings = response.json()["rankings"]
        self.assertEqual(rankings, [])
