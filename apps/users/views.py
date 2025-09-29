from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import JsonResponse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    ChangePasswordSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserSignUpSerializer,
)

User = get_user_model()


@swagger_auto_schema(methods=["post"], request_body=UserSignUpSerializer)
@api_view(["POST", "OPTIONS"])
@permission_classes([AllowAny])
def register(request):
    """일반 회원가입"""
    serializer = UserSignUpSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_link = f"{settings.FRONT_BASE_URL}/activate?uid={uid}&token={token}"

        send_mail(
            "회원가입 이메일 인증",
            f"다음 링크를 눌러 계정을 활성화하세요: {activation_link}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        return Response({"message": "인증 메일이 발송되었습니다."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    methods=["post"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "email": openapi.Schema(type=openapi.TYPE_STRING),
            "password": openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=["email", "password"],
    ),
    responses={
        200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "access": openapi.Schema(type=openapi.TYPE_STRING),
                "refresh": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=["access", "refresh"],
        )
    },
)
@api_view(["POST", "OPTIONS"])
@permission_classes([AllowAny])
def login(request):
    """일반 로그인"""
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response(
            {"error": "이메일과 비밀번호를 입력해주세요."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {"error": "이메일 또는 비밀번호가 올바르지 않습니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not user.check_password(password):
        return Response(
            {"error": "이메일 또는 비밀번호가 올바르지 않습니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not user.is_active:
        return Response(
            {"error": "비활성화된 계정입니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token

    # settings에서 설정된 시간 사용
    access_lifetime = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
    refresh_lifetime = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()

    response = JsonResponse({"success": True, "user": UserLoginSerializer(user).data})
    response.set_cookie(
        "access_token",
        str(access_token),
        max_age=int(access_lifetime),
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )
    response.set_cookie(
        "refresh_token",
        str(refresh),
        max_age=int(refresh_lifetime),
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )
    return response


@api_view(["POST", "OPTIONS"])
@permission_classes([IsAuthenticated])
def logout(request):
    """로그아웃 - 쿠키 삭제 및 리프레시 토큰 블랙리스트 처리"""
    try:
        # 쿠키에서 refresh_token 가져오기
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        response = JsonResponse({"message": "로그아웃되었습니다."})
        response.delete_cookie("access_token", samesite=settings.COOKIE_SAMESITE)
        response.delete_cookie("refresh_token", samesite=settings.COOKIE_SAMESITE)
        return response

    except Exception:
        response = JsonResponse({"error": "로그아웃 처리 중 오류가 발생했습니다."}, status=400)
        response.delete_cookie("access_token", samesite=settings.COOKIE_SAMESITE)
        response.delete_cookie("refresh_token", samesite=settings.COOKIE_SAMESITE)
        return response


@swagger_auto_schema(
    methods=["put"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "name": openapi.Schema(type=openapi.TYPE_STRING),
            "address": openapi.Schema(type=openapi.TYPE_STRING),
        },
    ),
)
@api_view(["GET", "PUT", "OPTIONS"])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """사용자 프로필 조회 및 수정"""
    user = request.user

    if request.method == "GET":
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE", "OPTIONS"])
@permission_classes([IsAuthenticated])
def user_delete(request):
    """회원 탈퇴"""
    user = request.user
    user.delete()
    response = Response({"message": "회원탈퇴가 완료되었습니다."}, status=status.HTTP_200_OK)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response


@swagger_auto_schema(methods=["put"], request_body=ChangePasswordSerializer)
@api_view(["PUT", "OPTIONS"])
@permission_classes([IsAuthenticated])
def change_password(request):
    """비밀번호 변경"""
    user = request.user

    # 소셜 로그인 사용자는 비밀번호 변경 불가
    if user.is_social:
        return Response(
            {"error": "소셜 로그인 사용자는 비밀번호를 변경할 수 없습니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        # 기존 비밀번호 확인
        if not user.check_password(old_password):
            return Response(
                {"error": "기존 비밀번호가 올바르지 않습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 새 비밀번호 설정
        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "비밀번호가 성공적으로 변경되었습니다."},
            status=status.HTTP_200_OK,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="post",
    request_body=PasswordResetRequestSerializer,  # ✅ 기존 serializer 사용
    responses={
        200: openapi.Response(
            "성공", examples={"application/json": {"message": "비밀번호 재설정 메일이 발송되었습니다."}}
        ),
        404: openapi.Response(
            "사용자 없음", examples={"application/json": {"error": "해당 이메일의 사용자가 없습니다."}}
        ),
        400: "유효성 검사 실패",
    },
)
@api_view(["POST", "OPTIONS"])
@permission_classes([AllowAny])
def password_reset_request(request):
    """비밀번호 재설정 메일 발송"""
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "해당 이메일의 사용자가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        if user.is_social:
            return Response(
                {"error": "소셜 로그인 사용자는 비밀번호 재설정을 할 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = f"{settings.FRONT_BASE_URL}/password-reset/confirm?uid={uid}&token={token}"

        send_mail(
            "비밀번호 재설정",
            f"다음 링크에서 비밀번호를 재설정하세요: {reset_link}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        return Response({"message": "비밀번호 재설정 메일이 발송되었습니다."})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="get",
    manual_parameters=[
        openapi.Parameter("uid", openapi.IN_QUERY, description="사용자 ID(Base64)", type=openapi.TYPE_STRING),
        openapi.Parameter("token", openapi.IN_QUERY, description="토큰", type=openapi.TYPE_STRING),
    ],
    responses={
        200: openapi.Response("성공", examples={"application/json": {"message": "계정이 활성화되었습니다."}}),
        400: "잘못된 링크 또는 유효하지 않은 토큰",
    },
)
@api_view(["GET", "OPTIONS"])
@permission_classes([AllowAny])
def activate_user(request):
    uidb64 = request.GET.get("uid")
    token = request.GET.get("token")

    if not uidb64 or not token:
        return Response({"error": "uid 또는 token이 누락되었습니다."}, status=status.HTTP_400_BAD_REQUEST)

    """이메일 인증"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({"error": "잘못된 링크입니다."}, status=status.HTTP_400_BAD_REQUEST)

    if default_token_generator.check_token(user, token):
        if not user.is_active:  # 이미 활성화된 유저라면 중복 처리 방지
            user.is_active = True
            user.save()
        return Response({"message": "계정이 활성화되었습니다."}, status=status.HTTP_200_OK)
    return Response({"error": "유효하지 않은 토큰입니다."}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="post",
    request_body=PasswordResetConfirmSerializer,
    manual_parameters=[
        openapi.Parameter("uid", openapi.IN_QUERY, description="사용자 ID Base64", type=openapi.TYPE_STRING),
        openapi.Parameter("token", openapi.IN_QUERY, description="토큰", type=openapi.TYPE_STRING),
    ],
    responses={
        200: openapi.Response(
            "성공", examples={"application/json": {"message": "비밀번호가 성공적으로 재설정되었습니다."}}
        ),
        400: "잘못된 링크 또는 유효하지 않은 토큰",
    },
)
@api_view(["POST", "OPTIONS"])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """
    비밀번호 재설정 (쿼리 파라미터 기반)
    예: /api/user/password-reset/confirm/?uid=abc123&token=xyz456
    """
    uidb64 = request.GET.get("uid")
    token = request.GET.get("token")

    if not uidb64 or not token:
        return Response({"error": "uid 또는 token이 누락되었습니다."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({"error": "잘못된 링크입니다."}, status=status.HTTP_400_BAD_REQUEST)

    if not default_token_generator.check_token(user, token):
        return Response({"error": "유효하지 않은 토큰입니다."}, status=status.HTTP_400_BAD_REQUEST)

    if user.is_social:
        return Response(
            {"error": "소셜 로그인 사용자는 비밀번호를 재설정할 수 없습니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        new_password = serializer.validated_data["new_password"]
        user.set_password(new_password)
        user.save()
        return Response({"message": "비밀번호가 성공적으로 재설정되었습니다."}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST", "OPTIONS"])
@permission_classes([AllowAny])
def token_refresh(request):
    """쿠키 기반 토큰 갱신"""
    refresh_token = request.COOKIES.get("refresh_token")

    if not refresh_token:
        return Response({"error": "Refresh token not found"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        refresh = RefreshToken(refresh_token)
        new_access_token = refresh.access_token

        # ROTATE_REFRESH_TOKENS=True라면 새 refresh token도 받음
        new_refresh_token = str(refresh)

        access_lifetime = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()
        refresh_lifetime = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()

        response = JsonResponse({"success": True})
        response.set_cookie(
            "access_token",
            str(new_access_token),
            max_age=int(access_lifetime),
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
        )
        response.set_cookie(
            "refresh_token",
            new_refresh_token,
            max_age=int(refresh_lifetime),
            httponly=True,
            secure=settings.COOKIE_SECURE,
            samesite=settings.COOKIE_SAMESITE,
        )
        return response

    except Exception:
        return Response({"error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)
