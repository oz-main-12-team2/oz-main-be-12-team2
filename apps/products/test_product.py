# /apps/products/test_product.py

from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase  # TestCase 대신 APITestCase를 기본으로 사용

from apps.orders.models import Order, OrderItem
from .models import Product

User = get_user_model()


class ProductModelTest(APITestCase):
    """Product 모델의 기본 동작을 테스트합니다."""

    def test_product_creation(self):
        """상품 모델이 정상적으로 생성되는지 테스트합니다."""
        product = Product.objects.create(name="테스트 상품", description="테스트 설명", author="테스트 작가", price="19.99", stock=100)
        self.assertEqual(product.name, "테스트 상품")

    def test_product_string_representation(self):
        """상품 모델의 __str__ 메서드가 상품명을 반환하는지 테스트합니다."""
        product = Product.objects.create(name="테스트 상품", price="10.00", stock=50)
        self.assertEqual(str(product), "테스트 상품")


class ProductViewTest(APITestCase):
    """일반 사용자용 상품 목록 및 상세 뷰를 테스트합니다."""

    @classmethod
    def setUpTestData(cls):
        """테스트에 필요한 상품 데이터를 미리 생성합니다."""
        # #- setUp 대신 setUpTestData를 사용해 불필요한 DB 접근을 줄입니다.
        cls.product1 = Product.objects.create(name="상품 1", price="10.0", stock=100)
        cls.list_url = reverse("products:product_list")
        cls.detail_url = reverse("products:product_detail", args=[cls.product1.pk])
        cls.not_found_url = reverse("products:product_detail", args=[9999])

    def test_product_list_view(self):
        """상품 목록 뷰가 정상적으로 상품 리스트를 반환하는지 테스트합니다."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.product1.name)

    def test_product_detail_view_success(self):
        """상품 상세 뷰가 특정 상품 정보를 정확히 반환하는지 테스트합니다."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.product1.name)

    def test_product_detail_view_not_found(self):
        """존재하지 않는 상품에 대해 404 에러를 반환하는지 테스트합니다."""
        response = self.client.get(self.not_found_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AdminViewTest(APITestCase):
    """관리자 기능 (상품 CRUD 및 통계)을 통합하여 테스트합니다."""

    @classmethod
    def setUpTestData(cls):
        """테스트에 필요한 유저, 상품, 주문 등 공통 데이터를 설정합니다."""
        cls.admin_user = User.objects.create_superuser(email="admin@example.com", name="관리자", password="adminpass")
        cls.normal_user = User.objects.create_user(email="user@example.com", name="일반사용자", password="userpass")
        cls.product_for_crud = Product.objects.create(name="수정 전 상품", price="5000", stock=20, author="작가")
        product_for_stats1 = Product.objects.create(name="통계용 상품 A", price="10000", stock=10)
        Product.objects.create(name="통계용 상품 B", price="25000", stock=5)

        # 테스트용 주문 데이터 생성
        mock_today = timezone.make_aware(datetime(2025, 9, 15, 10, 0, 0))
        order_today = Order.objects.create(user=cls.normal_user, status='배송완료', total_price=0) #order관련 에러 토탈값 우선 0설정
        OrderItem.objects.create(order=order_today, product=product_for_stats1, quantity=2, unit_price=product_for_stats1.price)
        order_today.created_at = mock_today
        order_today.save()

        order_5_days_ago = Order.objects.create(user=cls.normal_user, status='배송완료', total_price=0) #order관련 에러 토탈값 우선 0설정
        OrderItem.objects.create(order=order_5_days_ago, product=product_for_stats1, quantity=3, unit_price=product_for_stats1.price)
        order_5_days_ago.created_at = mock_today - timedelta(days=5)
        order_5_days_ago.save()

        # URL 미리 정의
        cls.create_url = reverse("products_admin:admin_product_create")
        cls.update_url = reverse("products_admin:admin_product_update", args=[cls.product_for_crud.pk])
        cls.delete_url = reverse("products_admin:admin_product_delete", args=[cls.product_for_crud.pk])
        cls.stats_url = reverse("products_admin:admin_sales_stats")

    def setUp(self):
        """각 테스트 실행 전, 관리자로 로그인한 클라이언트를 준비합니다."""
        # #- 실제 로그인 API를 호출하는 대신, force_authenticate로 직접 인증하여 테스트를 더 빠르고 안정적으로 만듭니다.
        self.client.force_authenticate(user=self.admin_user)

    # === 상품 CRUD API 테스트 ===
    def test_admin_product_create_success(self):
        """관리자가 상품을 성공적으로 생성하는지 테스트합니다."""
        data = {"name": "새 상품", "price": "20000", "stock": 10, "author": "새 작가"}
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Product.objects.filter(name="새 상품").exists())

    def test_admin_product_update_success(self):
        """관리자가 상품 정보를 성공적으로 수정하는지 테스트합니다."""
        data = {"name": "수정된 상품", "price": "9999"}
        response = self.client.patch(self.update_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product_for_crud.refresh_from_db()
        self.assertEqual(self.product_for_crud.name, "수정된 상품")

    def test_admin_product_delete_success(self):
        """관리자가 상품을 성공적으로 삭제하는지 테스트합니다."""
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(pk=self.product_for_crud.pk).exists())

    # === 판매 통계 API 테스트 ===
    def test_stats_api_admin_access_success(self):
        """관리자가 판매 통계 API에 접근할 수 있는지 테스트합니다."""
        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_stats_api_normal_user_access_forbidden(self):
        """일반 사용자가 판매 통계 API에 접근할 수 없는지(403 Forbidden) 테스트합니다."""
        # #- 테스트 목적에 맞게 일반 유저로 클라이언트를 잠시 교체합니다.
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("django.utils.timezone.now", return_value=timezone.make_aware(datetime(2025, 9, 15, 10, 0, 0)))
    def test_stats_api_stock_calculations(self, mock_now):
        """판매 통계 API의 재고 관련 계산이 정확한지 테스트합니다."""
        response = self.client.get(self.stats_url)
        data = response.data["stock_status"]

        expected_total_value = (5000 * 20) + (10000 * 10) + (25000 * 5)
        self.assertEqual(int(Decimal(data["total_stock_value"])), expected_total_value)
        self.assertEqual(data["on_sale_count"], 3)

    @patch("django.utils.timezone.now", return_value=timezone.make_aware(datetime(2025, 9, 15, 10, 0, 0)))
    def test_stats_api_sales_calculations(self, mock_now):
        """판매 통계 API의 판매량 관련 계산이 정확한지 테스트합니다."""
        response = self.client.get(self.stats_url)
        data = response.data["sales_statistics"]

        self.assertEqual(data["today"], 2)
        self.assertEqual(data["last_30_days"], 5)
        self.assertEqual(data["this_month"], 5)