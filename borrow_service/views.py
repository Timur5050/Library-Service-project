import requests

from django.conf import settings
from django.http import Http404
from rest_framework import mixins
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from book_service.models import Book
from borrow_service.models import Borrow
from borrow_service.serializers import (
    BorrowListSerializer,
    BorrowRetrieveSerializer, BorrowCreateSerializer
)


def send_message_to_telegram_group(message: str):
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    message = message

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message
    }
    return requests.post(url, data=payload)


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
            book.inventory -= 1
            book.save()
            send_message_to_telegram_group(
                f"{request.user.email}\nhas borrowed book: `{book.title}`\ntill {request.data["expected_return_date"]}"
            )
            return self.create(request, *args, **kwargs)

        raise Http404("No such books available")


class BorrowRetrieveView(
    mixins.RetrieveModelMixin,
    GenericAPIView
):
    serializer_class = BorrowRetrieveSerializer

    def get_object(self):
        return Borrow.objects.get(id=self.kwargs["pk"])

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
