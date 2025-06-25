from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
# Create your models here.

class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)

    def __str__(self):
        return f"OTP for {self.user.email} - {self.otp}"

