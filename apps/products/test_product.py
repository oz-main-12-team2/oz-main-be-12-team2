# /apps/products/test_product.py

from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.orders.models import Order, OrderItem
from .models import Product

User = get_user_model()


class ProductModelTest(TestCase):
    """Product 모델의 기본 동작을 테스트합니다."""

    def test_product_creation(self):
        product = Product.objects.create(name="테스트 상품", description="테스트 설명", author="테스트 작가", price=19.99, stock=100)
        self.assertEqual(product.name, "테스트 상품")

    def test_product_string_representation(self):
        product = Product.objects.create(name="테스트 상품", price=10.00, stock=50)
        self.assertEqual(str(product), "테스트 상품")


class ProductViewTest(TestCase):
    """일반 사용자용 상품 목록 및 상세 뷰를 테스트합니다."""

    def setUp(self):
        self.client = APIClient()
        self.product1 = Product.objects.create(name="상품 1", price=10.0, stock=100)

    def test_product_list_view(self):
        url = reverse("products:product_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.product1.name)

    def test_product_detail_view_success(self):
        url = reverse("products:product_detail", args=[self.product1.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.product1.name)

    def test_product_detail_view_not_found(self):
        url = reverse("products:product_detail", args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# /apps/products/test_product.py 파일

# /apps/products/test_product.py 파일

class AdminViewTest(APITestCase):
    """관리자 기능 (상품 CRUD 및 통계)을 통합하여 테스트합니다."""

    @classmethod
    def setUpTestData(cls):
        """테스트 전체에서 사용할 공통 데이터를 설정합니다."""
        cls.admin_user = User.objects.create_superuser(
            email="admin@example.com", name="관리자", password="adminpass"
        )
        cls.client.force_authenticate(user=cls.admin_user)
        cls.normal_user = User.objects.create_user(
            email="user@example.com", name="일반사용자", password="userpass"
        )
        cls.product_for_crud = Product.objects.create(name="수정 전 상품", price=5000, stock=20, author="작가", image_url="http://example.com/crud.jpg")
        cls.product_for_stats1 = Product.objects.create(name="통계용 상품 A", price=10000, stock=10)
        cls.product_for_stats2 = Product.objects.create(name="통계용 상품 B", price=25000, stock=5)
        cls.mock_today = timezone.make_aware(datetime(2025, 9, 15, 10, 0, 0))

        order_today = Order.objects.create(user=cls.normal_user, status='배송완료', total_price=0)
        order_today.created_at = cls.mock_today
        order_item_today = OrderItem.objects.create(order=order_today, product=cls.product_for_stats1, quantity=2, unit_price=cls.product_for_stats1.price)
        order_today.total_price = order_item_today.total_price
        order_today.save()

        order_5_days_ago = Order.objects.create(user=cls.normal_user, status='배송완료', total_price=0)
        order_5_days_ago.created_at = cls.mock_today - timedelta(days=5)
        order_item_5_days_ago = OrderItem.objects.create(order=order_5_days_ago, product=cls.product_for_stats1, quantity=3, unit_price=cls.product_for_stats1.price)
        order_5_days_ago.total_price = order_item_5_days_ago.total_price
        order_5_days_ago.save()

    def setUp(self):
        """각 테스트 실행 전 client 및 URL을 설정하고, 관리자로 로그인하여 토큰을 발급받습니다."""
        self.client = APIClient()
        self.create_url = reverse("products_admin:admin_product_create")
        self.update_url = reverse("products_admin:admin_product_update", args=[self.product_for_crud.pk])
        self.delete_url = reverse("products_admin:admin_product_delete", args=[self.product_for_crud.pk])
        self.stats_url = reverse("products_admin:admin_sales_stats")
        
        login_url = reverse("user_login")
        login_data = {"email": "admin@example.com", "password": "adminpass"}
        response = self.client.post(login_url, login_data, format='json')
        
        # --- 바로 이 부분을 수정했습니다! ---
        self.access_token = response.data['access']
        # -----------------------------------

    # === 상품 CRUD API 테스트 ===
    def test_admin_product_create_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        data = {"name": "새 상품", "price": 20000, "stock": 10, "author": "새 작가", "image_url": "http://example.com/new.jpg"}
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_product_update_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        data = {
            "name": "수정된 상품", "price": 99.99, "author": self.product_for_crud.author,
            "stock": self.product_for_crud.stock, "image_url": self.product_for_crud.image_url,
        }
        response = self.client.patch(self.update_url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_product_delete_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # === 판매 통계 API 테스트 ===
    def test_stats_api_admin_access_success(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_stats_api_normal_user_access_forbidden(self):
        login_url = reverse("user_login")
        login_data = {"email": "user@example.com", "password": "userpass"}
        response = self.client.post(login_url, login_data, format='json')
        
        # --- 바로 이 부분을 수정했습니다! ---
        normal_user_token = response.data['access']
        # -----------------------------------

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {normal_user_token}')
        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("django.utils.timezone.now")
    def test_stats_api_stock_calculations(self, mock_now):
        mock_now.return_value = self.mock_today
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(self.stats_url)
        data = response.json()["stock_status"]

        expected_total_value = (5000 * 20) + (10000 * 10) + (25000 * 5)
        expected_on_sale_count = 3

        self.assertEqual(int(Decimal(data["total_stock_value"])), expected_total_value)
        self.assertEqual(data["on_sale_count"], expected_on_sale_count)

    @patch("django.utils.timezone.now")
    def test_stats_api_sales_calculations(self, mock_now):
        mock_now.return_value = self.mock_today
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.get(self.stats_url)
        data = response.json()["sales_statistics"]

        self.assertEqual(data["today"], 2)
        self.assertEqual(data["last_30_days"], 5)
        self.assertEqual(data["this_month"], 5)