from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets

from book_service.models import Book
from book_service.serializers import BookSerializer
from book_service.permissions import ReadOnlyOrAdminPermission


@extend_schema_view(
    list=extend_schema(
        summary="get list of books, allowed to everyone",
    ),
    retrieve=extend_schema(
        summary="retrieve book, allowed to everyone"
    ),
    update=extend_schema(
        summary="update book, allowed to admins only"
    ),
    partial_update=extend_schema(
        summary="partial update book, allowed to admins only",
    ),
    create=extend_schema(
        summary="create new book, allowed to admins only",
    ),
    destroy=extend_schema(
        summary="delete book, allowed to admins only",
    ),
)
class BookViewSet(viewsets.ModelViewSet):
    """
       A viewset for viewing and editing book instances.
       This viewset provides `list`, `retrieve`, `create`, `update`, and `destroy` actions for Book objects.
       """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = (ReadOnlyOrAdminPermission,)
