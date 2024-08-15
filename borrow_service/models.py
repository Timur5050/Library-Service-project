from django.contrib.auth import get_user_model
from django.db import models
from rest_framework.exceptions import ValidationError

from book_service.models import Book


class Borrow(models.Model):
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def clean(self):
        if self.actual_return_date and self.borrow_date > self.actual_return_date:
            raise ValidationError("You can not return book before you borrow it")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Borrow, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.borrow_date} - {self.user} - {self.actual_return_date}"
