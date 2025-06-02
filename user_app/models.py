from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class CustomerCreate(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    username = models.CharField(max_length=120 , blank=True)
    first_name = models.CharField(max_length=100 , blank=True , null=True)
    last_name  = models.CharField(max_length=100 , blank=True , null=True)
    age = models.IntegerField(null=True , blank=True)
    phone = models.CharField(max_length=12 , null=True , blank=True)
    email = models.EmailField(null=True,blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    profile_picture = models.ImageField(default='default_user_pic.jpg' ,blank=True , null=True)

    def __str__(self):
        if self.first_name == '' or self.last_name == '' or (self.first_name == None or self.last_name == None):
            name = 'user'
            return name
        else:
            return f'{self.first_name} {self.last_name}'


