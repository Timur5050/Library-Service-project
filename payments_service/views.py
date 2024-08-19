import datetime

import stripe
from django.conf import settings
from django.http import Http404
from django.shortcuts import redirect
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrow_service.models import Borrow
from borrow_service.serializers import BorrowCreateSerializer, BorrowRetrieveSerializer
from notifications_service.views import send_message_to_telegram_group
from payments_service.models import Payment
from payments_service.serializers import (
    PaymentListSerializer,
    PaymentRetrieveSerializer,
)

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentListView(ListModelMixin, GenericAPIView):
    """
    A view for listing all payment records associated with the authenticated user.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Payment.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(borrowing__user=self.request.user)

        return queryset

    @extend_schema(
        summary="get all your patments",
        responses={200: BorrowCreateSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class PaymentRetrieveView(RetrieveModelMixin, GenericAPIView):
    """
    A view to retrieve a specific payment record associated with the authenticated user.
    """
    serializer_class = PaymentRetrieveSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self, *args, **kwargs):
        queryset = Payment.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(borrowing__user=self.request.user)
        try:
            return queryset.get(pk=self.kwargs["pk"])
        except Payment.DoesNotExist:
            raise Http404

    @extend_schema(
        summary="get one of your payments",
        responses={200: BorrowCreateSerializer(many=False)}
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


def create_payment_session(payment):
    """
    Creates a Stripe checkout session for a payment and redirects the user to the Stripe payment page.
    """
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": payment.borrowing.book.title,
                    },
                    "unit_amount": int(payment.money_to_pay) * 100,
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=f"http://127.0.0.1:8000/api/v1/success/payment/{payment.id}/",
        cancel_url=f"http://127.0.0.1:8000/api/v1/cancel/payment/{payment.id}/",
    )

    payment.session_url = session.url
    payment.session_id = session.id
    payment.save()

    return redirect(session.url)


@api_view(["GET"])
def success_payment_session(request, payment_id: int):
    """
    Handles the success of a Stripe payment session, reduces the inventory of the book,
    updates the payment status, and notifies the Telegram group.
    """
    payment = Payment.objects.get(pk=payment_id)
    borrow = payment.borrowing
    book = borrow.book
    book.inventory -= 1
    book.save()
    payment.status = "PAID"
    payment.save()
    send_message_to_telegram_group(
        f"{request.user.email}\nhas borrowed book: `{book.title}`\ntill {borrow.expected_return_date}"
    )
    serializer = BorrowCreateSerializer(borrow)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def cancel_payment_session(request, payment_id: int):
    """
    Handles the cancellation of a Stripe payment session and deletes the associated borrow record.
    """
    payment = Payment.objects.get(pk=payment_id)
    borrow = Borrow.objects.get(id=payment.borrowing.id)
    borrow.delete()
    return Response(
        {"success": "FAIL. You have 24 hours to pay for that book"},
        status=status.HTTP_502_BAD_GATEWAY,
    )


def create_fine_session(payment):
    """
    Creates a Stripe checkout session for a fine payment and redirects the user to the Stripe payment page.
    """
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "fine for overdue",
                    },
                    "unit_amount": int(payment.money_to_pay) * 100,
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=f"http://127.0.0.1:8000/api/v1/success/fine/{payment.id}/",
        cancel_url="http://127.0.0.1:8000/api/v1/cancel/fine/",
    )

    payment.session_url = session.url
    payment.session_id = session.id
    payment.save()

    return redirect(session.url)


@api_view(["GET"])
def success_fine_session(request, payment_id: int):
    """
    Handles the success of a fine payment session, updates the inventory and borrowing records,
    and notifies the Telegram group about the book return.
    """
    payment = Payment.objects.get(pk=payment_id)
    payment.borrowing.book.inventory += 1
    payment.borrowing.book.save()
    payment.borrowing.actual_return_date = datetime.date.today()
    payment.borrowing.save()
    payment.status = "PAID"
    payment.save()
    send_message_to_telegram_group(
        f"{request.user.email}\nhas returned book: "
        f"`{payment.borrowing.book.title}`\nexpected return date is : "
        f"{payment.borrowing.expected_return_date}\nactual return date is : {payment.borrowing.actual_return_date}"
    )
    serializer = BorrowRetrieveSerializer(payment.borrowing)
    return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


@api_view(["GET"])
def cancel_fine_session(request):
    """
    Handles the cancellation of a fine payment session.
    """
    return Response(
        {"success": "FAIL. You have 24 hours to pay for fine that borrowing"},
        status=status.HTTP_502_BAD_GATEWAY,
    )
