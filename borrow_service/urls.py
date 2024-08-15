from django.urls import path

from borrow_service.views import (
    BorrowListView,
    BorrowRetrieveView,
)

urlpatterns = [
    path("borrows/", BorrowListView.as_view(), name="borrows"),
    path("borrows/<int:pk>/", BorrowRetrieveView.as_view(), name="borrows"),
]

app_name = "borrow_service"
