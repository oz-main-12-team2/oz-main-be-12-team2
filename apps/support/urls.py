from django.urls import path

from . import views

urlpatterns = [
    # 문의 관련
    path('inquiries/', views.InquiryListCreateAPIView.as_view(), name='inquiry-list-create'),
    path('inquiries/<int:pk>/', views.InquiryDetailAPIView.as_view(), name='inquiry-detail'),
    path('inquiries/<int:inquiry_id>/replies/', views.InquiryReplyCreateAPIView.as_view(), name='inquiry-reply-create'),

    # FAQ
    path('faqs/', views.FAQListAPIView.as_view(), name='faq-list'),
]