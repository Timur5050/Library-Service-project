from django.contrib.auth import get_user_model
from django.db import models

from book_service.models import Book


class Borrow(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.borrow_date} - {self.user} - {self.actual_return_date}"
