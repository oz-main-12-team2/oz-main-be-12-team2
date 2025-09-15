
import json
from datetime import date, timedelta

from django.db.models import Sum
from django.test import Client, TestCase
from django.urls import reverse

from .admin_views import admin_product_create, admin_product_delete, admin_product_update
from .models import Product
from .stats_views import admin_sales_stats


# `views.py`에서 필요한 OrderItem, Order 모델을 모킹하기 위해 임시로 정의
class MockOrder(object):
    def __init__(self, status):
        self.status = status

class MockOrderItem(object):
    def __init__(self, product, quantity):
        self.product = product
        self.quantity = quantity
    
# Django TestCase를 상속받아 테스트 클래스 생성
class ProductModelTest(TestCase):
    def test_product_creation(self):
        """유효한 데이터로 상품이 성공적으로 생성되는지 테스트"""
        product = Product.objects.create(
            name="테스트 상품",
            description="테스트 설명",
            author="테스트 작가",
            price=19.99,
            stock=100,
        )
        self.assertEqual(product.name, "테스트 상품")
        self.assertEqual(product.stock, 100)
        self.assertTrue(product.created_at)
    
    def test_product_string_representation(self):
        """상품 객체의 __str__ 메서드가 올바르게 작동하는지 테스트"""
        product = Product.objects.create(name="테스트 상품", price=10.00, stock=50)
        self.assertEqual(str(product), "테스트 상품")

class ProductViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.product1 = Product.objects.create(
            name="상품 1", price=10.0, stock=100
        )
        self.product2 = Product.objects.create(
            name="상품 2", price=20.0, stock=50
        )
    
    # 이 테스트는 `views.py`의 랭킹 로직이 DB에 의존하므로, 실제 DB 데이터를 사용합니다.
    def test_product_list_view(self):
        """product_list 뷰가 정상적으로 렌더링되는지 테스트"""
        response = self.client.get(reverse('products:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product1.name)
        self.assertContains(response, self.product2.name)

    def test_product_detail_view_success(self):
        """유효한 pk로 product_detail 뷰 접근 시 200 OK 반환하는지 테스트"""
        response = self.client.get(reverse('products:product_detail', args=[self.product1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product1.name)

    def test_product_detail_view_not_found(self):
        """존재하지 않는 pk로 접근 시 404 Not Found 반환하는지 테스트"""
        response = self.client.get(reverse('products:product_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)

class AdminViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(
            name="수정 전 상품", price=5000, stock=20
        )
        self.create_url = reverse('products_admin:admin_product_create')
        self.update_url = reverse('products_admin:admin_product_update', args=[self.product.pk])
        self.delete_url = reverse('products_admin:admin_product_delete', args=[self.product.pk])
        self.stats_url = reverse('products_admin:admin_sales_stats')
        
    def test_admin_product_create_success(self):
        """상품 생성 API에 유효한 데이터로 요청 시 201 Created 반환하는지 테스트"""
        data = {
            "name": "새로운 상품",
            "description": "새 상품 설명",
            "author": "김작가",
            "price": "25.50",
            "stock": 50,
            "image_url": "http://example.com/image.jpg", #추가
        }
        response = self.client.post(self.create_url, data, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 2)

    def test_admin_product_create_invalid_data(self):
        """상품 생성 API에 유효하지 않은 데이터로 요청 시 400 Bad Request 반환하는지 테스트"""
        data = {"name": "", "price": "invalid"}  # 이름과 가격이 유효하지 않은 데이터
        response = self.client.post(self.create_url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('name', response.json()['errors'])
    
    def test_admin_product_update_success(self):
        """상품 수정 API에 유효한 데이터로 요청 시 200 OK 반환하는지 테스트"""
        data = {"name": "수정된 상품", 
                "price": 99.99,
                "author": self.product.author,
                "stock": self.product.stock,
                "image_url": self.product.image_url,
            }
        response = self.client.patch(self.update_url, data, content_type='application/json') #patch로수정
        self.assertEqual(response.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "수정된 상품")
    
    def test_admin_product_delete_success(self):
        """상품 삭제 API에 요청 시 200 OK와 함께 상품이 삭제되는지 테스트"""
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())
    
    def test_admin_product_delete_not_found(self):
        """존재하지 않는 상품 삭제 요청 시 404 Not Found 반환하는지 테스트"""
        response = self.client.post(reverse('products_admin:admin_product_delete', args=[9999]))
        self.assertEqual(response.status_code, 404)
        
    def test_admin_sales_stats_view(self):
        """판매 통계 API가 정상적으로 응답하는지 테스트"""
        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.json())
        self.assertIn("total_revenue", response.json()["data"])

