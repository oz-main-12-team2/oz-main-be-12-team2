from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User


class TokenRefreshTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="test@example.com", name="테스트유저", password="testpass123")
        self.user.is_active = True
        self.user.save()
        self.refresh_token = RefreshToken.for_user(self.user)
        self.url = reverse("token_refresh")

    def test_refresh_token_missing(self):
        """refresh_token 쿠키 누락"""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Refresh token not found")

    def test_refresh_token_success(self):
        """정상 토큰 갱신"""
        self.client.cookies["refresh_token"] = str(self.refresh_token)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["success"])
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

    def test_refresh_token_invalid(self):
        """잘못된 refresh_token"""
        self.client.cookies["refresh_token"] = "invalid_token"
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Invalid refresh token")
