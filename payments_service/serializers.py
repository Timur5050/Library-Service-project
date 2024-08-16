from rest_framework import serializers

from payments_service.models import Payment
from borrow_service.serializers import BorrowRetrieveSerializer


class PaymentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay"
        )


class PaymentRetrieveSerializer(serializers.ModelSerializer):
    borrowing = BorrowRetrieveSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "money_to_pay"
        )
