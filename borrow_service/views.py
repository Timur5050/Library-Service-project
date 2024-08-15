from rest_framework import mixins
from rest_framework.generics import GenericAPIView, RetrieveAPIView

from borrow_service.models import Borrow
from borrow_service.serializers import (
    BorrowListSerializer,
    BorrowRetrieveSerializer
)


class BorrowListView(
    mixins.ListModelMixin,
    GenericAPIView
):
    queryset = Borrow.objects.all()
    serializer_class = BorrowListSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class BorrowRetrieveView(
    mixins.RetrieveModelMixin,
    GenericAPIView
):
    serializer_class = BorrowRetrieveSerializer

    def get_object(self):
        return Borrow.objects.get(id=self.kwargs["pk"])

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
