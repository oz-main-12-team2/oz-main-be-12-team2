from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import FAQ, Inquiry
from .serializers import FAQSerializer, InquiryDetailSerializer, InquiryListSerializer, AdminInquiryUpdateSerializer


class AdminInquiryListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InquiryListSerializer
    queryset = Inquiry.objects.all()

    def check_admin_permission(self, user):
        """관리자 권한 체크"""
        if not user.is_admin:
            return Response({"error": "관리자만 접근 가능합니다."}, status=status.HTTP_403_FORBIDDEN)
        return None

    def list(self, request, *args, **kwargs):
        perm_check = self.check_admin_permission(request.user)
        if perm_check:
            return perm_check
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Inquiry.objects.all()
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset


class AdminInquiryDetailUpdateAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Inquiry.objects.all()

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return AdminInquiryUpdateSerializer  # 수정 시
        return InquiryDetailSerializer # 조회 시

    def check_admin_permission(self, user):
        """관리자 권한 체크"""
        if not user.is_admin:
            return Response({"error": "관리자만 접근 가능합니다."}, status=status.HTTP_403_FORBIDDEN)
        return None

    def retrieve(self, request, *args, **kwargs):
        perm_check = self.check_admin_permission(request.user)
        if perm_check:
            return perm_check
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        perm_check = self.check_admin_permission(request.user)
        if perm_check:
            return perm_check
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        perm_check = self.check_admin_permission(request.user)
        if perm_check:
            return perm_check
        return super().partial_update(request, *args, **kwargs)


class AdminFAQListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FAQSerializer
    queryset = FAQ.objects.all()

    def check_admin_permission(self, user):
        """관리자 권한 체크"""
        if not user.is_admin:
            return Response({"error": "관리자만 접근 가능합니다."}, status=status.HTTP_403_FORBIDDEN)
        return None

    def list(self, request, *args, **kwargs):
        perm_check = self.check_admin_permission(request.user)
        if perm_check:
            return perm_check
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        perm_check = self.check_admin_permission(request.user)
        if perm_check:
            return perm_check
        return super().create(request, *args, **kwargs)


class AdminFAQDetailUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FAQSerializer
    queryset = FAQ.objects.all()

    def check_admin_permission(self, user):
        """관리자 권한 체크"""
        if not user.is_admin:
            return Response({"error": "관리자만 접근 가능합니다."}, status=status.HTTP_403_FORBIDDEN)
        return None

    def retrieve(self, request, *args, **kwargs):
        perm_check = self.check_admin_permission(request.user)
        if perm_check:
            return perm_check
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        perm_check = self.check_admin_permission(request.user)
        if perm_check:
            return perm_check
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        perm_check = self.check_admin_permission(request.user)
        if perm_check:
            return perm_check
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        perm_check = self.check_admin_permission(request.user)
        if perm_check:
            return perm_check
        return super().destroy(request, *args, **kwargs)
