import datetime

from django.http import Http404
from rest_framework import mixins, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from book_service.models import Book
from borrow_service.models import Borrow
from borrow_service.serializers import (
    BorrowListSerializer,
    BorrowRetrieveSerializer, BorrowCreateSerializer
)

from notifications_service.views import send_message_to_telegram_group
from payments_service.models import Payment
from payments_service.views import create_payment_session


class BorrowListView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericAPIView
):
    queryset = Borrow.objects.all()
    serializer = BorrowListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Borrow.objects.all()
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        else:
            user_id = self.request.query_params.get("user_id", None)
            if user_id:
                queryset = queryset.filter(user_id=user_id)

        is_active = self.request.query_params.get("is_active", None)
        if is_active is not None:
            if is_active == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active == "false":
                queryset = queryset.filter(actual_return_date__isnull=False)
            else:
                raise Http404("You can pass only true or false to is_active query parameter")

        return queryset

    def get_serializer_class(self):
        serializer = self.serializer
        if self.request.method == "POST":
            serializer = BorrowCreateSerializer

        return serializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        book = Book.objects.get(pk=request.data["book"])
        if book.inventory > 0:
            serializer = BorrowCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.validated_data["user"] = request.user
            borrow = serializer.save()
            year, month, day = map(int, request.data["expected_return_date"].split("-"))
            date = datetime.date(year, month, day)
            payment = Payment.objects.create(
                status="PENDING",
                type="PAYMENT",
                borrowing=borrow,
                money_to_pay=(date - datetime.date.today()).days * book.daily_fee
            )
            return create_payment_session(payment)

        raise Http404("No such books available")


class BorrowRetrieveView(
    mixins.RetrieveModelMixin,
    GenericAPIView
):
    serializer_class = BorrowRetrieveSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return Borrow.objects.filter(user=self.request.user).get(id=self.kwargs["pk"])

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def return_borrowed_book(request: Request, borrow_id: int) -> Response:
    borrow = get_object_or_404(Borrow, id=borrow_id)
    if borrow.user != request.user:
        raise Http404("You do not have such borrow")

    book = borrow.book
    book.inventory += 1
    book.save()
    borrow.actual_return_date = datetime.date.today()
    borrow.save()
    serializer = BorrowRetrieveSerializer(borrow)
    send_message_to_telegram_group(
        f"{request.user.email}\nhas returned book: `{book.title}`\nexpected return date is : {borrow.expected_return_date}\nactual return date is : {borrow.actual_return_date}"
    )
    return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
