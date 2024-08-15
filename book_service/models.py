from django.db import models


class Book(models.Model):
    class Cover(models.TextChoices):
        HARD = "HARD",
        SOFT = "SOFT"

    title = models.CharField(max_length=100)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=4, choices=Cover.choices)
    inventory = models.IntegerField()
    daily_fee = models.DecimalField(max_digits=5, decimal_places=2)
