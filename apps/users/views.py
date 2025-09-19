from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
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
    UserProfileSerializer,
    UserSignUpSerializer,
)

User = get_user_model()


@swagger_auto_schema(methods=["post"], request_body=UserSignUpSerializer)
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """일반 회원가입"""
    serializer = UserSignUpSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_link = f"http://example.com/activate/{uid}/{token}/"  # TODO: 추후 프론트엔드 도메인으로 수정

        send_mail(
            "회원가입 이메일 인증",
            f"다음 링크를 눌러 계정을 활성화하세요: {activation_link}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        return Response({"message": "인증 메일이 발송되었습니다."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([AllowAny])
def activate_user(request, uidb64, token):
    """이메일 인증"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({"error": "잘못된 링크입니다."}, status=status.HTTP_400_BAD_REQUEST)

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return Response({"message": "계정이 활성화되었습니다."}, status=status.HTTP_200_OK)
    return Response({"error": "유효하지 않은 토큰입니다."}, status=status.HTTP_400_BAD_REQUEST)


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
@api_view(["POST"])
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

    user = authenticate(username=email, password=password)
    if user:
        # 비활성계정 체크기능 , 장고기본 설정상 체크 불가능 + 보안상의 이유로 체크 안하는것을 권장
        # if not user.is_active:
        #     return Response({"error": "비활성화된 계정입니다."}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        )

    return Response(
        {"error": "이메일 또는 비밀번호가 올바르지 않습니다."},
        status=status.HTTP_400_BAD_REQUEST,
    )


@swagger_auto_schema(
    methods=["post"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "refresh": openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=["refresh"],
    ),
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    """로그아웃 - 리프레시 토큰 블랙리스트 처리"""
    try:
        refresh_token = request.data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        return Response({"message": "로그아웃되었습니다."}, status=status.HTTP_200_OK)
    except Exception:
        return Response(
            {"error": "로그아웃 처리 중 오류가 발생했습니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )


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
@api_view(["GET", "PUT"])
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


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def user_delete(request):
    """회원 탈퇴"""
    user = request.user
    user.delete()
    return Response({"message": "회원탈퇴가 완료되었습니다."}, status=status.HTTP_200_OK)


@swagger_auto_schema(methods=["put"], request_body=ChangePasswordSerializer)
@api_view(["PUT"])
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
@api_view(["POST"])
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

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = (
            f"http://example.com/password-reset/confirm/{uid}/{token}/"  # TODO: 추후 프론트엔드 도메인으로 수정
        )

        send_mail(
            "비밀번호 재설정",
            f"다음 링크에서 비밀번호를 재설정하세요: {reset_link}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        return Response({"message": "비밀번호 재설정 메일이 발송되었습니다."})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="post",
    request_body=PasswordResetConfirmSerializer,  # ✅ 기존 serializer 사용
    manual_parameters=[
        openapi.Parameter("uidb64", openapi.IN_PATH, description="사용자 ID Base64", type=openapi.TYPE_STRING),
        openapi.Parameter("token", openapi.IN_PATH, description="토큰", type=openapi.TYPE_STRING),
    ],
    responses={
        200: openapi.Response(
            "성공", examples={"application/json": {"message": "비밀번호가 성공적으로 재설정되었습니다."}}
        ),
        400: "잘못된 링크 또는 유효하지 않은 토큰",
    },
)
@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_confirm(request, uidb64, token):
    """비밀번호 재설정"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({"error": "잘못된 링크입니다."}, status=status.HTTP_400_BAD_REQUEST)

    if not default_token_generator.check_token(user, token):
        return Response({"error": "유효하지 않은 토큰입니다."}, status=status.HTTP_400_BAD_REQUEST)

    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        new_password = serializer.validated_data["new_password"]
        user.set_password(new_password)
        user.save()
        return Response({"message": "비밀번호가 성공적으로 재설정되었습니다."})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
