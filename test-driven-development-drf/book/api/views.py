from rest_framework import viewsets, permissions, authentication
from rest_framework import mixins
from book.models import Book
from book.api import serializers


class BookViewSet(viewsets.ModelViewSet):
    """manages the book"""

    queryset = Book.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (authentication.TokenAuthentication,)
    serializer_class = serializers.BookSerializer
    lookup_url_kwarg = "book_id"

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)
