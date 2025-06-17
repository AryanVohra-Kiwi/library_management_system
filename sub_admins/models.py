from django.db import models
from django.contrib.auth.models import User, Permission


# Create your models here.
class SubAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    permissions = models.ManyToManyField(Permission)
    class Meta:
        permissions = [
            ('ReadBook','can read book'),
            ('UpdateBook' , 'can update book'),
            ('DeleteBook' , 'can delete book'),
        ]