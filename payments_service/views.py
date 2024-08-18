import datetime

import stripe
from django.conf import settings
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from book_service.models import Book
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
    queryset = Payment.objects.all()
    serializer_class = PaymentListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Payment.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(borrowing__user=self.request.user)

        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class PaymentRetrieveView(RetrieveModelMixin, GenericAPIView):
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

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


def create_payment_session(payment):
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
    payment = Payment.objects.get(pk=payment_id)
    borrow = Borrow.objects.get(id=payment.borrowing.id)
    borrow.delete()
    return Response(
        {"success": "FAIL. You have 24 hours to pay for that book"},
        status=status.HTTP_502_BAD_GATEWAY,
    )


def create_fine_session(payment):
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
    return Response(
        {"success": "FAIL. You have 24 hours to pay for fine that borrowing"},
        status=status.HTTP_502_BAD_GATEWAY,
    )
