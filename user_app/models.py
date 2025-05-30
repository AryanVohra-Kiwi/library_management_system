from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class CustomerCreate(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE , null=True)
    username = models.CharField(max_length=120 , blank=True)
    name = models.CharField(max_length=100)
    age = models.IntegerField(null=True , blank=True)
    phone = models.IntegerField(null=True , blank=True)
    email = models.EmailField(blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

