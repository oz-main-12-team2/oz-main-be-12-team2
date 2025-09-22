# 일반 사용자용 뷰들
from rest_framework import generics, permissions

from .models import FAQ, Inquiry
from .serializers import (
    FAQSerializer,
    InquiryCreateSerializer,
    InquiryDetailSerializer,
    InquiryListSerializer,
)


class InquiryListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return InquiryCreateSerializer
        return InquiryListSerializer

    def get_queryset(self):
        return Inquiry.objects.filter(user=self.request.user)


class InquiryDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InquiryDetailSerializer

    def get_queryset(self):
        return Inquiry.objects.filter(user=self.request.user)


# class InquiryReplyCreateAPIView(generics.CreateAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = InquiryReplyCreateSerializer
#
#     def perform_create(self, serializer):
#         inquiry_id = self.kwargs["inquiry_id"]
#         inquiry = get_object_or_404(Inquiry, id=inquiry_id, user=self.request.user)
#         serializer.save(author=self.request.user, inquiry=inquiry, is_admin_reply=self.request.user.is_staff)


class FAQListAPIView(generics.ListAPIView):
    serializer_class = FAQSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = FAQ.objects.filter(is_active=True)
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category=category)
        return queryset
