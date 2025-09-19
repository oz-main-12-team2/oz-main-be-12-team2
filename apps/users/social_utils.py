import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class NaverOAuth:
    @staticmethod
    def get_access_token(code, state):
        """네이버 인증 코드로 액세스 토큰 받기"""
        url = "https://nid.naver.com/oauth2.0/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.NAVER_CLIENT_ID,
            "client_secret": settings.NAVER_CLIENT_SECRET,
            "redirect_uri": settings.NAVER_REDIRECT_URI,
            "code": code,
            "state": state,
        }

        try:
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return {"error": "network_error"}

    @staticmethod
    def get_user_info(access_token):
        """네이버 액세스 토큰으로 사용자 정보 받기"""
        url = "https://openapi.naver.com/v1/nid/me"
        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return {"resultcode": "network_error"}


class GoogleOAuth:
    @staticmethod
    def get_access_token(code):
        """구글 인증 코드로 액세스 토큰 받기"""
        url = "https://oauth2.googleapis.com/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        }

        try:
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return {"error": "network_error"}

    @staticmethod
    def get_user_info(access_token):
        """구글 액세스 토큰으로 사용자 정보 받기"""
        url = f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={access_token}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return {"error": "network_error"}


class SocialAuthService:
    @staticmethod
    def create_or_get_user(email, name):
        """소셜 정보로 사용자 생성 또는 가져오기"""
        try:
            # 이메일로 기존 사용자 찾기
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # 새 사용자 생성
            user = User.objects.create_user(email=email, name=name, is_social=True, is_active=True)

        return user

    @staticmethod
    def generate_jwt_tokens(user):
        """JWT 토큰 생성"""
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
