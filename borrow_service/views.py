import datetime

from django.conf import settings
from django.http import Http404
from drf_spectacular.utils import extend_schema_view, extend_schema
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
from payments_service.views import create_payment_session, create_fine_session


@extend_schema_view(
    list=extend_schema(
        summary="You can see your list of borrows",
    ),
    create=extend_schema(
        summary="You can create a new borrow",
    ),
)
class BorrowListView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericAPIView
):
    """
        A view for listing and creating borrow instances.

        This view handles two actions:
            - Listing all the borrow records for the authenticated user.
            - Creating a new borrow instance for an authenticated user.
    """
    queryset = Borrow.objects.all()
    serializer = BorrowListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Retrieves the queryset of borrow records. If the user is not an admin,
        it returns only the records associated with the user. It can be further filtered
        by the `is_active` query parameter to show active or inactive borrow records.
        """
        queryset = Borrow.objects.all().select_related("book")
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
        """
        Returns the serializer class based on the HTTP method.
        Uses `BorrowListSerializer` for GET requests and `BorrowCreateSerializer` for POST requests.
        """
        serializer = self.serializer
        if self.request.method == "POST":
            serializer = BorrowCreateSerializer

        return serializer

    @extend_schema(
        summary="list all your borrows",
        responses={200: BorrowListSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @extend_schema(
        summary="create new borrow",
        responses={200: BorrowCreateSerializer(many=True)}
    )
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
    """
    A view to retrieve a single borrow instance for the authenticated user.
    This view allows an authenticated user to retrieve details of a specific borrow record.
    """
    serializer_class = BorrowRetrieveSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            return Borrow.objects.filter(user=self.request.user).get(id=self.kwargs["pk"])
        except Exception:
            raise Http404

    @extend_schema(
        summary="retrieve one of your borrows",
        responses={200: BorrowCreateSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


@extend_schema(
    summary="return one of books that you taken",
    responses={200: BorrowCreateSerializer(many=True)}
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def return_borrowed_book(request: Request, borrow_id: int) -> Response:
    """
    Handles the return process for a borrowed book.
    It checks whether the borrow instance belongs to the authenticated user and calculates
    potential fines if the book is returned late. It updates the borrow record with the actual
    return date and sends a notification to a Telegram group.
    """
    borrow = get_object_or_404(Borrow, id=borrow_id)
    if borrow.user != request.user:
        raise Http404("You do not have such borrow")

    today_date = datetime.date.today()

    if borrow.expected_return_date < today_date:
        payment = Payment.objects.create(
            status="PENDING",
            type="FINE",
            borrowing=borrow,
            money_to_pay=
            settings.FINE_MULTIPLIER * (
                    today_date - borrow.expected_return_date
            ).days
        )
        return create_fine_session(payment)
    book = borrow.book
    book.inventory += 1
    book.save()
    borrow.actual_return_date = today_date
    borrow.save()
    serializer = BorrowRetrieveSerializer(borrow)
    send_message_to_telegram_group(
        f"{request.user.email}\nhas returned book: `{book.title}`\nexpected return date is : {borrow.expected_return_date}\nactual return date is : {borrow.actual_return_date}"
    )
    return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
