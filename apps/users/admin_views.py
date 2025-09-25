from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.utils.pagination import CustomPagination

from .models import User
from .serializers import AdminUserSerializer, AdminUserUpdateSerializer


class IsAdmin:
    """관리자 권한 체크 커스텀 Permission"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


@api_view(["GET", "OPTIONS"])
@permission_classes([IsAuthenticated])
def admin_user_list(request):
    """전체 사용자 조회 - 관리자 전용"""
    if not request.user.is_admin:
        return Response({"error": "관리자만 접근 가능합니다."}, status=status.HTTP_403_FORBIDDEN)

    users = User.objects.all().order_by("-created_at")
    paginator = CustomPagination()
    paginated_users = paginator.paginate_queryset(users, request)
    serializer = AdminUserSerializer(paginated_users, many=True)
    return paginator.get_paginated_response(serializer.data)


class AdminUserDetailView(APIView):
    """관리자 전용 사용자 상세 조회/수정/삭제"""

    permission_classes = [IsAuthenticated]

    def check_admin_permission(self, user):
        """관리자 권한 체크"""
        if not user.is_admin:
            return Response({"error": "관리자만 접근 가능합니다."}, status=status.HTTP_403_FORBIDDEN)
        return None

    def get(self, request, user_id):
        """특정 사용자 상세 조회"""
        admin_check = self.check_admin_permission(request.user)
        if admin_check:
            return admin_check

        user = get_object_or_404(User, id=user_id)
        serializer = AdminUserSerializer(user)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=AdminUserUpdateSerializer,
        responses={200: AdminUserSerializer, 400: "Bad Request", 403: "Forbidden"},
    )
    def put(self, request, user_id):
        """특정 사용자 정보 수정"""
        admin_check = self.check_admin_permission(request.user)
        if admin_check:
            return admin_check

        user = get_object_or_404(User, id=user_id)
        serializer = AdminUserUpdateSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(AdminUserSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, user_id):
        """특정 사용자 삭제"""
        admin_check = self.check_admin_permission(request.user)
        if admin_check:
            return admin_check

        user = get_object_or_404(User, id=user_id)

        # 자기 자신은 삭제할 수 없음
        if user.id == request.user.id:
            return Response(
                {"error": "자기 자신은 삭제할 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.delete()
        return Response(
            {"message": f"사용자 {user.email}이 삭제되었습니다."},
            status=status.HTTP_200_OK,
        )
