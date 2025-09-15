from django.urls import path

from .views import PaymentCreateView, UserPaymentDetailView, UserPaymentListView

urlpatterns = [
    path("", PaymentCreateView.as_view(), name="payment-create"),
    path("my/", UserPaymentListView.as_view(), name="user-payment-list"),
    path("<int:pk>/", UserPaymentDetailView.as_view(), name="user-payment-detail"),
]
