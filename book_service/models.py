from typing import Any

from django.db import models
from rest_framework.exceptions import ValidationError


class Book(models.Model):
    class Cover(models.TextChoices):
        HARD = "HARD"
        SOFT = "SOFT"

    title = models.CharField(max_length=100)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=4, choices=Cover.choices)
    inventory = models.IntegerField()
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)

    def clean(self):
        if self.daily_fee < 0:
            raise ValidationError("Daily fee cannot be negative")
        if self.inventory < 0:
            raise ValidationError("Inventory cannot be negative")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Book, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return str(self.title)
