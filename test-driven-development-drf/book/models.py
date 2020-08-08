from django.db import models
from django.conf import settings

# Create your models here.
class Book(models.Model):

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="books"
    )
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=200)
    status = models.BooleanField()

    def __str__(self):
        return self.name
