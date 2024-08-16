from django.urls import path

from payments_service.views import PaymentListView, PaymentRetrieveView

urlpatterns = [
    path("payments/", PaymentListView.as_view(), name="payments-list"),
    path("payments/<int:pk>/", PaymentRetrieveView.as_view(), name="payments-retrieve"),
]

app_name = "payment_service"
