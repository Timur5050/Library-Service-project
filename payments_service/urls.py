from django.urls import path

from payments_service.views import (
    PaymentListView,
    PaymentRetrieveView,
    success_payment_session,
    cancel_payment_session,
)

urlpatterns = [
    path("payments/", PaymentListView.as_view(), name="payments-list"),
    path("payments/<int:pk>/", PaymentRetrieveView.as_view(), name="payments-retrieve"),
    path("success/<int:payment_id>/", success_payment_session, name="payments-success"),
    path("cancel/<int:payment_id>/", cancel_payment_session, name="payments-cancel"),
]

app_name = "payment_service"
