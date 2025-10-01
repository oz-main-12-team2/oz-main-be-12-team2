from django.urls import path

from apps.payments.views.user_views import (
    PaymentCreateView,
    UserPaymentCancelView,
    UserPaymentDetailView,
    UserPaymentListView,
)

urlpatterns = [
    path("", PaymentCreateView.as_view(), name="payment-create"),
    path("my/", UserPaymentListView.as_view(), name="user-payment-list"),
    path("<int:pk>/", UserPaymentDetailView.as_view(), name="user-payment-detail"),
    path("<int:pk>/cancel/", UserPaymentCancelView.as_view(), name="user-payment-cancel"),
]
