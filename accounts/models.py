from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    dateofbirth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)


def __str__(self):
    return self.username
