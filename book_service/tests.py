from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from book_service.models import Book
from book_service.serializers import BookSerializer

books_url = reverse("book_service:book-list")


def create_book(pk) -> Book:
    return Book.objects.create(
        title=f"book{pk}",
        author="123",
        cover="HARD",
        inventory=100,
        daily_fee=10
    )


def detail_url(book_id):
    return reverse("book_service:book-detail", args=[book_id])


class TestUnauthenticatedUserBooks(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_unauthenticated_user(self):
        res = self.client.get(books_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class TestAuthenticatedUserBook(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test123@gmail.com",
            "test123"
        )
        self.client.force_authenticate(self.user)

    def test_list_books(self):
        res = self.client.get(books_url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 0)

        self.book1 = create_book(1)
        self.book2 = create_book(2)
        self.book3 = create_book(3)
        res = self.client.get(books_url)
        self.assertEqual(len(res.data), 3)

    def test_retrieve_book_details(self):
        book = create_book(1)

        url = detail_url(book.id)
        res = self.client.get(url)

        serializer = BookSerializer(book)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_book_forbidden(self):
        data = {
            "title": "book",
            "author": "123",
            "cover": "HARD",
            "inventory": 100,
            "daily_fee": 10
        }

        res = self.client.post(books_url, data)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class TestAdminUserBook(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "test123@gmail.com",
            "test123",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self):
        data = {
            "title": "book",
            "author": "123",
            "cover": "HARD",
            "inventory": 100,
            "daily_fee": 10
        }

        res = self.client.post(books_url, data, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
