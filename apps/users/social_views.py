import secrets

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .social_utils import GoogleOAuth, NaverOAuth, SocialAuthService


class NaverLoginStartView(APIView):
    def get(self, request):
        """네이버 OAuth 로그인 시작"""
        state = secrets.token_urlsafe(32)

        auth_url = (
            f"https://nid.naver.com/oauth2.0/authorize"
            f"?response_type=code"
            f"&client_id={settings.NAVER_CLIENT_ID}"
            f"&redirect_uri={settings.NAVER_REDIRECT_URI}"
            f"&state={state}"
        )

        # state를 세션에 저장 (CSRF 방지)
        request.session["naver_oauth_state"] = state

        return HttpResponseRedirect(auth_url)


class NaverLoginCallbackView(APIView):
    def get(self, request):
        """네이버 OAuth 콜백 처리"""
        code = request.GET.get("code")
        state = request.GET.get("state")

        if not code or not state:
            return Response({"error": "코드와 상태값이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # state 검증
        stored_state = request.session.get("naver_oauth_state")
        if state != stored_state:
            return Response({"error": "잘못된 요청입니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. 액세스 토큰 받기
            token_response = NaverOAuth.get_access_token(code, state)

            if "access_token" not in token_response:
                return Response({"error": "네이버 토큰 발급 실패"}, status=status.HTTP_400_BAD_REQUEST)

            access_token = token_response["access_token"]

            # 2. 사용자 정보 받기
            user_info = NaverOAuth.get_user_info(access_token)

            if user_info.get("resultcode") != "00":
                return Response({"error": "네이버 사용자 정보 조회 실패"}, status=status.HTTP_400_BAD_REQUEST)

            # 네이버는 response 안에 사용자 정보가 있음
            user_data = user_info["response"]

            # 3. 사용자 생성 또는 가져오기
            user = SocialAuthService.create_or_get_user(
                email=user_data.get("email"),
                name=user_data.get("name"),
            )

            # 4. JWT 토큰 생성
            tokens = SocialAuthService.generate_jwt_tokens(user)

            # 쿠키로 토큰 설정
            access_lifetime = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
            refresh_lifetime = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()

            response = redirect(settings.FRONT_BASE_URL)
            response.set_cookie(
                "access_token",
                tokens["access"],
                max_age=int(access_lifetime),
                httponly=True,
                secure=settings.COOKIE_SECURE,
                samesite=settings.COOKIE_SAMESITE,
            )
            response.set_cookie(
                "refresh_token",
                tokens["refresh"],
                max_age=int(refresh_lifetime),
                httponly=True,
                secure=settings.COOKIE_SECURE,
                samesite=settings.COOKIE_SAMESITE,
            )
            return response

        except Exception:
            return Response(
                {"error": "네이버 로그인 처리 중 오류가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            # state 정리
            request.session.pop("naver_oauth_state", None)
            request.session.save()


class GoogleLoginStartView(APIView):
    def get(self, request):
        """구글 OAuth 로그인 시작"""
        state = secrets.token_urlsafe(32)

        auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth"
            f"?response_type=code"
            f"&client_id={settings.GOOGLE_CLIENT_ID}"
            f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
            f"&scope=openid email profile"
            f"&state={state}"
        )

        # state를 세션에 저장 (CSRF 방지)
        request.session["google_oauth_state"] = state

        return HttpResponseRedirect(auth_url)


class GoogleLoginCallbackView(APIView):
    def get(self, request):
        """구글 OAuth 콜백 처리"""
        code = request.GET.get("code")
        state = request.GET.get("state")

        if not code or not state:
            return Response({"error": "인증 코드가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # state 검증
        stored_state = request.session.get("google_oauth_state")
        if state != stored_state:
            return Response({"error": "잘못된 요청입니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. 액세스 토큰 받기
            token_response = GoogleOAuth.get_access_token(code)

            if "access_token" not in token_response:
                return Response({"error": "구글 토큰 발급 실패"}, status=status.HTTP_400_BAD_REQUEST)

            access_token = token_response["access_token"]

            # 2. 사용자 정보 받기
            user_info = GoogleOAuth.get_user_info(access_token)

            if "error" in user_info:
                return Response({"error": "구글 사용자 정보 조회 실패"}, status=status.HTTP_400_BAD_REQUEST)

            # 3. 사용자 생성 또는 가져오기
            user = SocialAuthService.create_or_get_user(
                email=user_info.get("email"),
                name=user_info.get("name"),
            )

            # 4. JWT 토큰 생성
            tokens = SocialAuthService.generate_jwt_tokens(user)

            # 쿠키로 토큰 설정
            access_lifetime = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
            refresh_lifetime = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()

            response = redirect(settings.FRONT_BASE_URL)
            response.set_cookie(
                "access_token",
                tokens["access"],
                max_age=int(access_lifetime),
                httponly=True,
                secure=settings.COOKIE_SECURE,
                samesite=settings.COOKIE_SAMESITE,
            )
            response.set_cookie(
                "refresh_token",
                tokens["refresh"],
                max_age=int(refresh_lifetime),
                httponly=True,
                secure=settings.COOKIE_SECURE,
                samesite=settings.COOKIE_SAMESITE,
            )
            return response

        except Exception:
            response = Response(
                {"error": "구글 로그인 처리 중 오류가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        finally:
            # state 정리
            request.session.pop("google_oauth_state", None)
            request.session.save()

        return response
