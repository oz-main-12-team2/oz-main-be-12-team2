from unittest.mock import Mock, patch

import requests
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.social_utils import GoogleOAuth, NaverOAuth, SocialAuthService

User = get_user_model()


@override_settings(
    NAVER_CLIENT_ID="test_naver_id",
    NAVER_CLIENT_SECRET="test_naver_secret",
    NAVER_REDIRECT_URI="http://localhost:8000/auth/naver/callback",
    GOOGLE_CLIENT_ID="test_google_id",
    GOOGLE_CLIENT_SECRET="test_google_secret",
    GOOGLE_REDIRECT_URI="http://localhost:8000/auth/google/callback",
)
class NaverOAuthTest(TestCase):
    @patch("apps.users.social_utils.requests.post")
    def test_get_access_token_success(self, mock_post):
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.json.return_value = {"access_token": "test_access_token", "token_type": "bearer"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # 테스트 실행
        result = NaverOAuth.get_access_token("test_code", "test_state")

        # 검증
        self.assertEqual(result["access_token"], "test_access_token")
        mock_post.assert_called_once_with(
            "https://nid.naver.com/oauth2.0/token",
            data={
                "grant_type": "authorization_code",
                "client_id": "test_naver_id",
                "client_secret": "test_naver_secret",
                "redirect_uri": "http://localhost:8000/auth/naver/callback",
                "code": "test_code",
                "state": "test_state",
            },
            timeout=10,
        )

    @patch("apps.users.social_utils.requests.post")
    def test_get_access_token_network_error(self, mock_post):
        # Mock 네트워크 에러
        mock_post.side_effect = requests.RequestException("Network error")

        # 테스트 실행
        result = NaverOAuth.get_access_token("test_code", "test_state")

        # 검증
        self.assertEqual(result, {"error": "network_error"})

    @patch("apps.users.social_utils.requests.get")
    def test_get_user_info_success(self, mock_get):
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": {"id": "123", "email": "test@naver.com", "name": "테스터"},
            "resultcode": "00",
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # 테스트 실행
        result = NaverOAuth.get_user_info("test_access_token")

        # 검증
        self.assertEqual(result["response"]["email"], "test@naver.com")
        mock_get.assert_called_once_with(
            "https://openapi.naver.com/v1/nid/me", headers={"Authorization": "Bearer test_access_token"}, timeout=10
        )

    @patch("apps.users.social_utils.requests.get")
    def test_get_user_info_network_error(self, mock_get):
        # Mock 네트워크 에러
        mock_get.side_effect = requests.RequestException("Network error")

        # 테스트 실행
        result = NaverOAuth.get_user_info("test_access_token")

        # 검증
        self.assertEqual(result, {"resultcode": "network_error"})


@override_settings(
    GOOGLE_CLIENT_ID="test_google_id",
    GOOGLE_CLIENT_SECRET="test_google_secret",
    GOOGLE_REDIRECT_URI="http://localhost:8000/auth/google/callback",
)
class GoogleOAuthTest(TestCase):
    @patch("apps.users.social_utils.requests.post")
    def test_get_access_token_success(self, mock_post):
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.json.return_value = {"access_token": "test_google_token", "token_type": "Bearer"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # 테스트 실행
        result = GoogleOAuth.get_access_token("test_code")

        # 검증
        self.assertEqual(result["access_token"], "test_google_token")
        mock_post.assert_called_once_with(
            "https://oauth2.googleapis.com/token",
            data={
                "grant_type": "authorization_code",
                "client_id": "test_google_id",
                "client_secret": "test_google_secret",
                "code": "test_code",
                "redirect_uri": "http://localhost:8000/auth/google/callback",
            },
            timeout=10,
        )

    @patch("apps.users.social_utils.requests.post")
    def test_get_access_token_network_error(self, mock_post):
        # Mock 네트워크 에러
        mock_post.side_effect = requests.RequestException("Network error")

        # 테스트 실행
        result = GoogleOAuth.get_access_token("test_code")

        # 검증
        self.assertEqual(result, {"error": "network_error"})

    @patch("apps.users.social_utils.requests.get")
    def test_get_user_info_success(self, mock_get):
        # Mock 응답 설정
        mock_response = Mock()
        mock_response.json.return_value = {"id": "123456789", "email": "test@gmail.com", "name": "Test User"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # 테스트 실행
        result = GoogleOAuth.get_user_info("test_access_token")

        # 검증
        self.assertEqual(result["email"], "test@gmail.com")
        mock_get.assert_called_once_with(
            "https://www.googleapis.com/oauth2/v2/userinfo?access_token=test_access_token", timeout=10
        )

    @patch("apps.users.social_utils.requests.get")
    def test_get_user_info_network_error(self, mock_get):
        # Mock 네트워크 에러
        mock_get.side_effect = requests.RequestException("Network error")

        # 테스트 실행
        result = GoogleOAuth.get_user_info("test_access_token")

        # 검증
        self.assertEqual(result, {"error": "network_error"})


class SocialAuthServiceTest(TestCase):
    def test_create_or_get_user_existing_user(self):
        # 기존 사용자 생성 (소셜 사용자)
        existing_user = User.objects.create(email="test@example.com", name="Existing User", is_social=True)

        # 테스트 실행
        user = SocialAuthService.create_or_get_user("test@example.com", "New Name")

        # 검증
        self.assertEqual(user.id, existing_user.id)
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.name, "Existing User")  # 기존 이름 유지
        self.assertEqual(User.objects.count(), 1)

    def test_create_or_get_user_new_user(self):
        # 테스트 실행
        user = SocialAuthService.create_or_get_user("new@example.com", "New User")

        # 검증
        self.assertEqual(user.email, "new@example.com")
        self.assertEqual(user.name, "New User")
        self.assertTrue(user.is_social)
        self.assertEqual(User.objects.count(), 1)

    def test_generate_jwt_tokens(self):
        # 사용자 생성 (소셜 사용자)
        user = User.objects.create(email="test@example.com", name="Test User", is_social=True, is_active=True)

        # 테스트 실행
        tokens = SocialAuthService.generate_jwt_tokens(user)

        # 검증
        self.assertIn("refresh", tokens)
        self.assertIn("access", tokens)
        self.assertIsInstance(tokens["refresh"], str)
        self.assertIsInstance(tokens["access"], str)

        # JWT 토큰 검증
        refresh_token = RefreshToken(tokens["refresh"])
        self.assertEqual(refresh_token["user_id"], str(user.id))
