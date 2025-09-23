# apps/products/test_products.py

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Product

User = get_user_model()


class BaseProductTestCase(APITestCase):
    """Product 테스트 공통 데이터 설정"""

    @classmethod
    def setUpTestData(cls):
        # 사용자
        cls.admin_user = User.objects.create_superuser(email="admin@example.com", name="관리자", password="adminpass")
        cls.normal_user = User.objects.create_user(email="user@example.com", name="일반사용자", password="userpass")

        # 상품
        cls.product = Product.objects.create(name="테스트 상품", price=Decimal("10000.00"), stock=10, author="작가")

        # URL
        cls.list_url = reverse("products:product-list")
        cls.detail_url = reverse("products:product-detail", args=[cls.product.pk])

        cls.admin_create_url = reverse("products_admin:admin_product_create")
        cls.admin_detail_url = reverse("products_admin:admin_product_detail_update_delete", args=[cls.product.pk])


class ProductPublicViewTest(BaseProductTestCase):
    """일반 사용자 상품 조회 뷰 테스트"""

    def test_product_list_view(self):
        """상품 목록 조회 성공"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.product.name)

    def test_product_detail_view(self):
        """상품 상세 조회 성공"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.product.name)


class ProductAdminViewTest(BaseProductTestCase):
    """관리자 상품 CRUD 테스트"""

    def setUp(self):
        # 각 테스트마다 관리자 인증
        self.client.force_authenticate(user=self.admin_user)

    def test_admin_create_product_success(self):
        """관리자가 상품을 생성할 수 있다"""
        data = {"name": "새 상품", "price": "20000.00", "stock": 5, "author": "새 작가"}
        response = self.client.post(self.admin_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Product.objects.filter(name="새 상품").exists())

    def test_admin_get_product_detail(self):
        """관리자가 상품 상세 조회 가능"""
        response = self.client.get(self.admin_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.product.name)

    def test_admin_update_product_success(self):
        """관리자가 상품 수정 가능"""
        data = {"name": "수정된 상품", "price": "15000.00", "stock": 20}
        response = self.client.put(self.admin_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "수정된 상품")
        self.assertEqual(self.product.price, Decimal("15000.00"))
        self.assertEqual(self.product.stock, 20)

    def test_admin_delete_product_success(self):
        """관리자가 상품 삭제 가능"""
        response = self.client.delete(self.admin_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())


class ProductPermissionTest(BaseProductTestCase):
    """권한 관련 테스트"""

    def test_normal_user_cannot_access_admin_api(self):
        """일반 사용자는 admin API 접근 불가"""
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.post(
            self.admin_create_url,
            {"name": "권한 테스트 상품", "price": "5000.00", "stock": 1},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ProductSearchAndOrderingTest(BaseProductTestCase):
    """상품 검색 및 정렬 테스트"""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # 추가 상품 데이터 생성
        cls.product1 = Product.objects.create(
            name="해리포터",
            description="마법사 이야기",
            author="조앤 롤링",
            category="소설",
            price=Decimal("15000.00"),
            stock=3,
        )
        cls.product2 = Product.objects.create(
            name="데이터베이스 설계",
            description="DB 교재",
            author="홍길동",
            category="IT",
            price=Decimal("30000.00"),
            stock=7,
        )
        cls.product3 = Product.objects.create(
            name="철학 입문",
            description="고대 철학자들",
            author="아리스토텔레스",
            category="인문",
            price=Decimal("10000.00"),
            stock=2,
        )

    def test_search_by_query_name(self):
        """query 파라미터로 상품명 검색"""
        response = self.client.get(self.list_url, {"query": "해리포터"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "해리포터")

    def test_search_by_query_author(self):
        """query 파라미터로 저자 검색"""
        response = self.client.get(self.list_url, {"query": "홍길동"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["author"], "홍길동")

    def test_filter_by_category(self):
        """카테고리 필터"""
        response = self.client.get(self.list_url, {"category": "인문"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["category"], "인문")

    def test_filter_by_price_range(self):
        """가격 범위 필터"""
        response = self.client.get(self.list_url, {"min_price": "12000", "max_price": "20000"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "해리포터")

    def test_ordering_by_price_asc(self):
        """가격 오름차순 정렬"""
        response = self.client.get(self.list_url, {"ordering": "price"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        prices = [Decimal(item["price"]) for item in response.data["results"]]
        self.assertEqual(prices, sorted(prices))

    def test_ordering_by_price_desc(self):
        """가격 내림차순 정렬"""
        response = self.client.get(self.list_url, {"ordering": "-price"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        prices = [Decimal(item["price"]) for item in response.data["results"]]
        self.assertEqual(prices, sorted(prices, reverse=True))
