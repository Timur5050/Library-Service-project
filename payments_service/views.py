from django.http import Http404
from django.shortcuts import render
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated

from payments_service.models import Payment
from payments_service.serializers import PaymentListSerializer, PaymentRetrieveSerializer


class PaymentListView(
    ListModelMixin, GenericAPIView
):
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


class PaymentRetrieveView(
    RetrieveModelMixin, GenericAPIView
):
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
