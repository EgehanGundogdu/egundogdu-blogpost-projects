from rest_framework import serializers
from book.models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["name", "author", "status"]
        read_only_fields = ("id", "owner")
