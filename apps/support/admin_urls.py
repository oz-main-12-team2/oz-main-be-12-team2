from django.urls import path

from . import admin_views

urlpatterns = [
    # 문의 관리
    path("inquiries/", admin_views.AdminInquiryListAPIView.as_view(), name="admin-inquiry-list"),
    path(
        "inquiries/<int:pk>/", admin_views.AdminInquiryDetailUpdateAPIView.as_view(), name="admin-inquiry-detail-update"
    ),
    # FAQ 관리
    path("faqs/", admin_views.AdminFAQListCreateAPIView.as_view(), name="admin-faq-list-create"),
    path(
        "faqs/<int:pk>/", admin_views.AdminFAQDetailUpdateDeleteAPIView.as_view(), name="admin-faq-detail-update-delete"
    ),
]
