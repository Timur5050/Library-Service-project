from django.urls import path

from borrow_service.views import (
    BorrowListView,
    BorrowRetrieveView,
    return_borrowed_book
)

urlpatterns = [
    path("borrows/", BorrowListView.as_view(), name="borrows"),
    path("borrows/<int:pk>/", BorrowRetrieveView.as_view(), name="borrows"),
    path("borrow/<int:borrow_id>/return/", return_borrowed_book, name="return_borrowed_book"),
]

app_name = "borrow_service"
