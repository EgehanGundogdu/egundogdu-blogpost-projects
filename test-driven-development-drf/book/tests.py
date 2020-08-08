from book.api.serializers import BookSerializer
from django.urls import reverse
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework import status
from book.models import Book
from rest_framework import serializers


def populate_book_url(book=None):
    if book is None:
        return reverse("book:book-list")
    return reverse("book:book-detail", kwargs={"book_id": book.id})


class PublicBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_books_unauthenticated(self):
        url = populate_book_url()
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBookApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="egehan", password="supersecret")
        cls.user_2 = User.objects.create_user(
            username="gundogdu", password="superpassword"
        )
        cls.token = Token.objects.create(user=cls.user)
        cls.token = Token.objects.create(user=cls.user_2)
        """setting up test data. user1 book"""
        cls.book = Book.objects.create(
            owner=cls.user, name="1984", author="George Orwell", status=True
        )
        cls.book1 = Book.objects.create(
            owner=cls.user,
            name="Harry Potter Deathly Hallows",
            author="J.K Rowling",
            status=False,
        )

        """user 2 book"""
        cls.book2 = Book.objects.create(
            owner=cls.user_2,
            name="Computer Networks and Internets",
            author="Dogulas E. Comer",
            status=False,
        )

    def test_list_owned_books(self):
        url = populate_book_url()

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user.auth_token.key}")
        res = self.client.get(url)
        serializer = BookSerializer(
            instance=Book.objects.filter(owner=self.user), many=True
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_new_book(self):
        url = populate_book_url()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user.auth_token.key}")
        #  or self.client.force_authenticate(self.user, self.user.auth_token.key)
        payload = {
            "name": "Harry Potter Half Blood Prince",
            "author": "J.K Rowling",
            "status": True,
        }
        res = self.client.post(url, data=payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.filter(owner=self.user).count(), 3)
        self.assertEqual(Book.objects.last().name, payload["name"])

    def test_update_owned_book(self):
        url = populate_book_url(self.book)
        self.client.force_authenticate(self.user)
        payload = {"status": False}

        res = self.client.patch(url, data=payload, format="json")

        self.book.refresh_from_db()
        self.assertFalse(self.book.status)

    def test_get_not_owned_book(self):
        url = populate_book_url(self.book2)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.user.auth_token.key}"
        )  # authenticate user1

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_new_book_wrong_payload(self):
        wrong_payload = {"name": "missed author name", "status": False}
        with self.assertRaisesMessage(
            serializers.ValidationError, "This field is required"
        ):
            serializer = BookSerializer(data=wrong_payload)
            serializer.is_valid(raise_exception=True)

    def test_delete_owned_book(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.user_2.auth_token.key}"
        )  # authenticate user2
        url = populate_book_url(self.book2)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.filter(owner=self.user_2).count(), 0)
