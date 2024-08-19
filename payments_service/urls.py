from django.urls import path

from payments_service.views import (
    PaymentListView,
    PaymentRetrieveView,
    success_payment_session,
    cancel_payment_session,
    success_fine_session,
    cancel_fine_session
)

urlpatterns = [
    path("payments/", PaymentListView.as_view(), name="payments-list"),
    path("payments/<int:pk>/", PaymentRetrieveView.as_view(), name="payments-retrieve"),
    path("success/payment/<int:payment_id>/", success_payment_session, name="payments-success"),
    path("cancel/payment/<int:payment_id>/", cancel_payment_session, name="payments-cancel"),
    path("success/fine/<int:payment_id>/", success_fine_session, name="fine-success"),
    path("cancel/fine/", cancel_fine_session, name="fine-cancel"),
]

app_name = "payment_service"
