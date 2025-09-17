from django.contrib.auth import authenticate
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import ChangePasswordSerializer, UserProfileSerializer, UserSignUpSerializer


@swagger_auto_schema(
    methods=["post"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "email": openapi.Schema(type=openapi.TYPE_STRING),
            "name": openapi.Schema(type=openapi.TYPE_STRING),
            "password": openapi.Schema(type=openapi.TYPE_STRING),
            "password_confirm": openapi.Schema(type=openapi.TYPE_STRING),
            "address": openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=["email", "name", "password", "password_confirm"],
    ),
)
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """일반 회원가입"""
    print(f"Request data: {request.data}")
    print(f"Content type: {request.content_type}")
    serializer = UserSignUpSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserProfileSerializer(user).data, status=status.HTTP_201_CREATED)
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
)
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """일반 로그인"""
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response({"error": "이메일과 비밀번호를 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=email, password=password)
    if user:
        # 비활성계정 체크기능 , 장고기본 설정상 체크 불가능 + 보안상의 이유로 체크 안하는것을 권장
        # if not user.is_active:
        #     return Response({"error": "비활성화된 계정입니다."}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        serializer = UserProfileSerializer(user)
        return Response(
            {
                "user": serializer.data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        )

    return Response({"error": "이메일 또는 비밀번호가 올바르지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)


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
        return Response({"error": "로그아웃 처리 중 오류가 발생했습니다."}, status=status.HTTP_400_BAD_REQUEST)


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


@swagger_auto_schema(
    methods=["put"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "old_password": openapi.Schema(type=openapi.TYPE_STRING),
            "new_password": openapi.Schema(type=openapi.TYPE_STRING),
            "new_password_confirm": openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=["old_password", "new_password", "new_password_confirm"],
    ),
)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def change_password(request):
    """비밀번호 변경"""
    user = request.user

    # 소셜 로그인 사용자는 비밀번호 변경 불가
    if user.is_social:
        return Response(
            {"error": "소셜 로그인 사용자는 비밀번호를 변경할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST
        )

    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        # 기존 비밀번호 확인
        if not user.check_password(old_password):
            return Response({"error": "기존 비밀번호가 올바르지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 새 비밀번호 설정
        user.set_password(new_password)
        user.save()

        return Response({"message": "비밀번호가 성공적으로 변경되었습니다."}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
