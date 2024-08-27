from django.db import models

from borrow_service.models import Borrow


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING"
        PAID = "PAID"

    class Type(models.TextChoices):
        PAYMENT = "PAYMENT"
        FINE = "FINE"

    status = models.CharField(max_length=20, choices=Status.choices)
    type = models.CharField(max_length=20, choices=Type.choices)
    borrowing = models.ForeignKey(Borrow, on_delete=models.CASCADE)
    session_url = models.URLField(max_length=500)
    session_id = models.CharField(max_length=500)
    money_to_pay = models.DecimalField(max_digits=10, decimal_places=2)
