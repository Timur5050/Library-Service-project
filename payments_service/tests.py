from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from book_service.models import Book
from borrow_service.models import Borrow
from payments_service.models import Payment

payment_url = reverse("payment_service:payments-list")


def create_borrow(book, user) -> Borrow:
    time = timezone.now()
    return Borrow.objects.create(
        borrow_date=time,
        expected_return_date=time,
        actual_return_date=time,
        book=book,
        user=user,
    )


def create_book(pk) -> Book:
    return Book.objects.create(
        title=f"book{pk}",
        author="123",
        cover="HARD",
        inventory=100,
        daily_fee=10
    )


def create_payment(pk, borrowing):
    return Payment.objects.create(
        status="PAID",
        type="PAYMENT",
        borrowing=borrowing,
        session_url=f"http://{pk}.png",
        session_id=f"{pk}",
        money_to_pay=2
    )


def detail_url(borrow_id):
    return reverse("payment_service:payments-retrieve", args=[borrow_id])


class TestUnauthenticatedUserPayments(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_user(self):
        res = self.client.get(payment_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestAuthenticatedUserPayment(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test123@gmail.com",
            "test123"
        )
        self.user2 = get_user_model().objects.create_user(
            "test1234@gmail.com",
            "test1234"
        )
        self.client.force_authenticate(self.user)

    def test_list_payments(self):
        res = self.client.get(payment_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 0)

        book = create_book(1)
        borrow1 = create_borrow(book, self.user)
        borrow2 = create_borrow(book, self.user2)
        borrow3 = create_borrow(book, self.user2)

        create_payment(1, borrow1)
        create_payment(2, borrow2)
        create_payment(3, borrow3)

        res = self.client.get(payment_url)
        self.assertEqual(len(res.data), 1)

    def test_retrieve_payments(self):
        book = create_book(1)
        borrow1 = create_borrow(book, self.user)
        borrow2 = create_borrow(book, self.user2)
        borrow3 = create_borrow(book, self.user2)

        payment1 = create_payment(1, borrow1)
        payment2 = create_payment(2, borrow2)
        payment3 = create_payment(3, borrow3)

        url1 = detail_url(payment1.pk)
        url2 = detail_url(payment2.pk)
        url3 = detail_url(payment3.pk)

        res = self.client.get(url1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self.client.get(url2)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        res = self.client.get(url3)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
