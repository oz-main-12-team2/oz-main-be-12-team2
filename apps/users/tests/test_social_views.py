from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import User


class SocialLoginTest(TestCase):
    """소셜 로그인 테스트"""

    def setUp(self):
        User.objects.all().delete()
        self.client = APIClient()

    # NaverLoginStartView 테스트 (라인 13-26)
    def test_naver_login_start_success(self):
        """네이버 로그인 시작 - 정상적으로 리다이렉트"""
        url = reverse("naver_login_start")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("nid.naver.com/oauth2.0/authorize", response.url)
        self.assertIn(f"client_id={settings.NAVER_CLIENT_ID}", response.url)
        self.assertIn("naver_oauth_state", self.client.session)

    @patch("apps.users.social_views.SocialAuthService.generate_jwt_tokens")
    @patch("apps.users.social_views.SocialAuthService.create_or_get_user")
    @patch("apps.users.social_views.NaverOAuth.get_user_info")
    @patch("apps.users.social_views.NaverOAuth.get_access_token")
    def test_naver_callback_success(self, mock_get_token, mock_get_user_info, mock_create_user, mock_generate_tokens):
        """네이버 콜백 - 성공적인 로그인"""
        # 세션 설정
        session = self.client.session
        session["naver_oauth_state"] = "test_state"
        session.save()

        # Mock 설정
        mock_get_token.return_value = {"access_token": "test_access_token"}
        mock_get_user_info.return_value = {
            "resultcode": "00",
            "response": {"email": "test@example.com", "name": "테스트 사용자"},
        }

        # 사용자 객체 생성
        test_user = User.objects.create_user(email="test@example.com", name="테스트 사용자", is_social=True)

        mock_create_user.return_value = test_user
        mock_generate_tokens.return_value = {"access": "mock_access_token", "refresh": "mock_refresh_token"}

        url = reverse("naver_login_callback")
        response = self.client.get(url, {"code": "test_code", "state": "test_state"})

        # 리다이렉트 응답 확인
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")

        # 쿠키 설정 확인
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

        # 쿠키 값 확인
        access_cookie = response.cookies["access_token"]
        refresh_cookie = response.cookies["refresh_token"]

        self.assertEqual(access_cookie.value, "mock_access_token")
        self.assertEqual(refresh_cookie.value, "mock_refresh_token")
        self.assertTrue(access_cookie["httponly"])
        self.assertTrue(refresh_cookie["httponly"])
        self.assertEqual(access_cookie["samesite"], settings.SESSION_COOKIE_SAMESITE)
        self.assertEqual(refresh_cookie["samesite"], settings.SESSION_COOKIE_SAMESITE)

        # 세션 정리 확인
        self.assertNotIn("naver_oauth_state", self.client.session)

        # Mock 호출 확인
        mock_create_user.assert_called_once_with(email="test@example.com", name="테스트 사용자")
        mock_generate_tokens.assert_called_once_with(test_user)

    # NaverLoginCallbackView 테스트 (라인 30-91)
    def test_naver_callback_missing_code_and_state(self):
        """네이버 콜백 - 코드와 상태값 누락"""
        url = reverse("naver_login_callback")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "코드와 상태값이 필요합니다.")

    def test_naver_callback_missing_code_only(self):
        """네이버 콜백 - 코드만 누락"""
        url = reverse("naver_login_callback")
        response = self.client.get(url, {"state": "test_state"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "코드와 상태값이 필요합니다.")

    def test_naver_callback_missing_state_only(self):
        """네이버 콜백 - 상태값만 누락"""
        url = reverse("naver_login_callback")
        response = self.client.get(url, {"code": "test_code"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "코드와 상태값이 필요합니다.")

    def test_naver_callback_invalid_state(self):
        """네이버 콜백 - 잘못된 상태값"""
        # 세션에 올바른 state 저장
        session = self.client.session
        session["naver_oauth_state"] = "valid_state"
        session.save()

        url = reverse("naver_login_callback")
        response = self.client.get(
            url,
            {
                "code": "test_code",
                "state": "invalid_state",  # 다른 state
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "잘못된 요청입니다.")

    @patch("apps.users.social_views.NaverOAuth.get_access_token")
    def test_naver_callback_token_failure(self, mock_get_token):
        """네이버 콜백 - 토큰 발급 실패"""
        # 세션 설정
        session = self.client.session
        session["naver_oauth_state"] = "test_state"
        session.save()

        # 토큰 발급 실패 응답
        mock_get_token.return_value = {"error": "invalid_grant"}

        url = reverse("naver_login_callback")
        response = self.client.get(url, {"code": "test_code", "state": "test_state"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "네이버 토큰 발급 실패")

    @patch("apps.users.social_views.NaverOAuth.get_user_info")
    @patch("apps.users.social_views.NaverOAuth.get_access_token")
    def test_naver_callback_user_info_failure(self, mock_get_token, mock_get_user_info):
        """네이버 콜백 - 사용자 정보 조회 실패"""
        # 세션 설정
        session = self.client.session
        session["naver_oauth_state"] = "test_state"
        session.save()

        # Mock 설정
        mock_get_token.return_value = {"access_token": "test_token"}
        mock_get_user_info.return_value = {"resultcode": "01"}  # 실패 코드

        url = reverse("naver_login_callback")
        response = self.client.get(url, {"code": "test_code", "state": "test_state"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "네이버 사용자 정보 조회 실패")

    @patch("apps.users.social_views.NaverOAuth.get_access_token")
    def test_naver_callback_exception_handling(self, mock_get_token):
        """네이버 콜백 - 예외 발생"""
        # 세션 설정
        session = self.client.session
        session["naver_oauth_state"] = "test_state"
        session.save()

        # 예외 발생 Mock
        mock_get_token.side_effect = Exception("네트워크 오류")

        url = reverse("naver_login_callback")
        response = self.client.get(url, {"code": "test_code", "state": "test_state"})

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["error"], "네이버 로그인 처리 중 오류가 발생했습니다.")

        # 세션 정리 확인
        self.assertNotIn("naver_oauth_state", self.client.session)

    # GoogleLoginStartView 테스트 (라인 95-109)
    def test_google_login_start_success(self):
        """구글 로그인 시작 - 정상적으로 리다이렉트"""
        url = reverse("google_login_start")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("accounts.google.com/o/oauth2/v2/auth", response.url)
        self.assertIn(f"client_id={settings.GOOGLE_CLIENT_ID}", response.url)

        # URL 파싱해서 scope 확인
        from urllib.parse import parse_qs, urlparse

        parsed = urlparse(response.url)
        params = parse_qs(parsed.query)
        self.assertEqual(params["scope"][0], "openid email profile")

        # 세션에 state 저장 확인
        self.assertIn("google_oauth_state", self.client.session)

        # state 파라미터가 URL에 포함되었는지 확인
        self.assertIn("state", params)
        self.assertEqual(params["state"][0], self.client.session["google_oauth_state"])

    @patch("apps.users.social_views.SocialAuthService.generate_jwt_tokens")
    @patch("apps.users.social_views.SocialAuthService.create_or_get_user")
    @patch("apps.users.social_views.GoogleOAuth.get_user_info")
    @patch("apps.users.social_views.GoogleOAuth.get_access_token")
    def test_google_callback_success(self, mock_get_token, mock_get_user_info, mock_create_user, mock_generate_tokens):
        """구글 콜백 - 성공적인 로그인"""
        # 세션 설정
        session = self.client.session
        session["google_oauth_state"] = "test_state"
        session.save()

        # Mock 설정
        mock_get_token.return_value = {"access_token": "test_access_token"}
        mock_get_user_info.return_value = {"email": "test@example.com", "name": "테스트 사용자"}

        # 사용자 객체 생성
        test_user = User.objects.create_user(email="test@example.com", name="테스트 사용자", is_social=True)

        mock_create_user.return_value = test_user
        mock_generate_tokens.return_value = {"access": "mock_access_token", "refresh": "mock_refresh_token"}

        url = reverse("google_login_callback")
        response = self.client.get(url, {"code": "test_code", "state": "test_state"})

        # 리다이렉트 응답 확인
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")

        # 쿠키 설정 확인
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

        # 쿠키 값 확인
        access_cookie = response.cookies["access_token"]
        refresh_cookie = response.cookies["refresh_token"]

        self.assertEqual(access_cookie.value, "mock_access_token")
        self.assertEqual(refresh_cookie.value, "mock_refresh_token")
        self.assertTrue(access_cookie["httponly"])
        self.assertTrue(refresh_cookie["httponly"])
        self.assertEqual(access_cookie["samesite"], settings.SESSION_COOKIE_SAMESITE)
        self.assertEqual(refresh_cookie["samesite"], settings.SESSION_COOKIE_SAMESITE)

        # 세션 정리 확인
        self.assertNotIn("google_oauth_state", self.client.session)

        # Mock 호출 확인
        mock_create_user.assert_called_once_with(email="test@example.com", name="테스트 사용자")
        mock_generate_tokens.assert_called_once_with(test_user)

    # GoogleLoginCallbackView 테스트 (라인 115-171)
    def test_google_callback_missing_code_and_state(self):
        """구글 콜백 - 코드와 상태값 누락"""
        url = reverse("google_login_callback")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "인증 코드가 필요합니다.")

    def test_google_callback_invalid_state(self):
        """구글 콜백 - 잘못된 상태값"""
        # 세션에 올바른 state 저장
        session = self.client.session
        session["google_oauth_state"] = "valid_state"
        session.save()

        url = reverse("google_login_callback")
        response = self.client.get(url, {"code": "test_code", "state": "invalid_state"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "잘못된 요청입니다.")

    @patch("apps.users.social_views.GoogleOAuth.get_access_token")
    def test_google_callback_token_failure(self, mock_get_token):
        """구글 콜백 - 토큰 발급 실패"""
        # 세션 설정
        session = self.client.session
        session["google_oauth_state"] = "test_state"
        session.save()

        # 토큰 발급 실패
        mock_get_token.return_value = {"error": "invalid_grant"}

        url = reverse("google_login_callback")
        response = self.client.get(url, {"code": "test_code", "state": "test_state"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "구글 토큰 발급 실패")

    @patch("apps.users.social_views.GoogleOAuth.get_user_info")
    @patch("apps.users.social_views.GoogleOAuth.get_access_token")
    def test_google_callback_user_info_failure(self, mock_get_token, mock_get_user_info):
        """구글 콜백 - 사용자 정보 조회 실패"""
        # 세션 설정
        session = self.client.session
        session["google_oauth_state"] = "test_state"
        session.save()

        # Mock 설정
        mock_get_token.return_value = {"access_token": "test_token"}
        mock_get_user_info.return_value = {"error": "invalid_token"}

        url = reverse("google_login_callback")
        response = self.client.get(url, {"code": "test_code", "state": "test_state"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "구글 사용자 정보 조회 실패")

    @patch("apps.users.social_views.GoogleOAuth.get_access_token")
    def test_google_callback_exception_handling(self, mock_get_token):
        """구글 콜백 - 예외 발생"""
        # 세션 설정
        session = self.client.session
        session["google_oauth_state"] = "test_state"
        session.save()

        # 예외 발생 Mock
        mock_get_token.side_effect = Exception("네트워크 오류")

        url = reverse("google_login_callback")
        response = self.client.get(url, {"code": "test_code", "state": "test_state"})

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["error"], "구글 로그인 처리 중 오류가 발생했습니다.")

        # 세션 정리 확인
        self.client.session.load()
        self.assertNotIn("google_oauth_state", self.client.session)
