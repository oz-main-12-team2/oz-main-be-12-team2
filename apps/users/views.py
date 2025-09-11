from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import SocialSignUpSerializer, UserProfileSerializer, UserSignUpSerializer, ChangePasswordSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """일반 회원가입"""
    print(f"Request data: {request.data}")
    print(f"Content type: {request.content_type}")
    serializer = UserSignUpSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            UserProfileSerializer(user).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """일반 로그인"""
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {'error': '이메일과 비밀번호를 입력해주세요.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=email, password=password)
    if user:
        if not user.is_active:
            return Response(
                {'error': '비활성화된 계정입니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })

    return Response(
        {'error': '이메일 또는 비밀번호가 올바르지 않습니다.'},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def google_login(request):
    """구글 소셜 로그인"""
    # TODO: 구글 토큰 검증 로직 구현 필요
    google_token = request.data.get('token')

    if not google_token:
        return Response(
            {'error': '구글 토큰이 필요합니다.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 구글 토큰 검증 및 사용자 정보 획득 로직
    # google_user_info = verify_google_token(google_token)

    # 임시 응답 (실제 구현 시 수정 필요)
    return Response(
        {'message': '구글 로그인 API - 구현 예정'},
        status=status.HTTP_501_NOT_IMPLEMENTED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def naver_login(request):
    """네이버 소셜 로그인"""
    # TODO: 네이버 토큰 검증 로직 구현 필요
    naver_token = request.data.get('token')

    if not naver_token:
        return Response(
            {'error': '네이버 토큰이 필요합니다.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 네이버 토큰 검증 및 사용자 정보 획득 로직
    # naver_user_info = verify_naver_token(naver_token)

    # 임시 응답 (실제 구현 시 수정 필요)
    return Response(
        {'message': '네이버 로그인 API - 구현 예정'},
        status=status.HTTP_501_NOT_IMPLEMENTED
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

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """사용자 프로필 조회 및 수정"""
    user = request.user

    if request.method == 'GET':
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def user_delete(request):
    """회원 탈퇴"""
    user = request.user
    user.delete()
    return Response(
        {'message': '회원탈퇴가 완료되었습니다.'},
        status=status.HTTP_200_OK
    )

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """비밀번호 변경"""
    user = request.user

    # 소셜 로그인 사용자는 비밀번호 변경 불가
    if user.is_social:
        return Response(
            {'error': '소셜 로그인 사용자는 비밀번호를 변경할 수 없습니다.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        # 기존 비밀번호 확인
        if not user.check_password(old_password):
            return Response(
                {'error': '기존 비밀번호가 올바르지 않습니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 새 비밀번호 설정
        user.set_password(new_password)
        user.save()

        return Response(
            {'message': '비밀번호가 성공적으로 변경되었습니다.'},
            status=status.HTTP_200_OK
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)