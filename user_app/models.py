from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class CustomerCreate(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE , related_name='profile')
    first_name = models.CharField(max_length=100 , blank=True , null=True)
    last_name  = models.CharField(max_length=100 , blank=True , null=True)
    age = models.IntegerField(null=True , blank=True)
    phone = models.CharField(max_length=15 , null=True , blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    profile_picture = models.ImageField(
        upload_to='profile_picture',
        default='default_user_pic.jpg' ,
        blank=True ,
        null=True
    )

    def __str__(self):
        full_name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        return full_name or self.user.username

    class Meta:
        verbose_name = 'Customer Profile'
        verbose_name_plural = "Customer Profiles"


