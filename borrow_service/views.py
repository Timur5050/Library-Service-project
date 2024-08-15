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


class BorrowListView(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericAPIView
):
    queryset = Borrow.objects.all()
    serializer = BorrowListSerializer
    permission_classes = (IsAuthenticated,)



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
