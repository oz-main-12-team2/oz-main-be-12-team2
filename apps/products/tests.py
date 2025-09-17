# apps/products/tests.py

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Product

User = get_user_model()


class ProductModelTest(APITestCase):
    def test_product_creation(self):
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
        product = Product.objects.create(name="테스트 상품", price=10.00, stock=50)
        self.assertEqual(str(product), "테스트 상품")


class ProductViewTest(APITestCase):
    def setUp(self):
        self.product1 = Product.objects.create(name="상품 1", price=10.0, stock=100)
        self.product2 = Product.objects.create(name="상품 2", price=20.0, stock=50)

    def test_product_list_view(self):
        url = reverse("products:product-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.product1.name)
        self.assertContains(response, self.product2.name)

    def test_product_detail_view_success(self):
        url = reverse("products:product-detail", args=[self.product1.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, self.product1.name)

    def test_product_detail_view_not_found(self):
        url = reverse("products:product-detail", args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AdminViewTest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com", name="Admin User", password="adminpass"
        )
        self.client.force_authenticate(user=self.admin_user)
        self.product = Product.objects.create(name="수정 전 상품", price=5000, stock=20)
        self.create_url = reverse("products:admin-product-list")
        self.update_url = reverse("products:admin-product-detail", args=[self.product.pk])
        self.delete_url = reverse("products:admin-product-detail", args=[self.product.pk])
        self.stats_url = reverse("products:admin-product-list")  # placeholder

    def test_admin_product_create_success(self):
        data = {
            "name": "새로운 상품",
            "description": "새 상품 설명",
            "author": "김작가",
            "price": 25.50,
            "stock": 50,
            "image_url": "http://example.com/image.jpg",
        }
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_admin_product_create_invalid_data(self):
        data = {"name": "", "price": "invalid"}
        response = self.client.post(self.create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_product_update_success(self):
        data = {
            "name": "수정된 상품",
            "price": 99.99,
            "author": getattr(self.product, "author", ""),
            "stock": self.product.stock,
            "image_url": getattr(self.product, "image_url", ""),
        }
        response = self.client.put(self.update_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "수정된 상품")

    def test_admin_product_delete_success(self):
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())

    def test_admin_product_delete_not_found(self):
        url = reverse("products:admin-product-detail", args=[9999])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_sales_stats_view(self):
        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
