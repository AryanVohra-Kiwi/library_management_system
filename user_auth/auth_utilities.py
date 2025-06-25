from django.core.mail import send_mail
from django.conf import settings
import random
from .models import EmailVerification
def send_email(send_to_email , otp_code):

    subject = "Verify Your Account: One-Time Password (OTP)"
    message = f"Your one time otp for verification is {otp_code}"
    from_email = settings.EMAIL_HOST_USER

    send_mail(subject=subject,
              message=message,
              from_email=from_email,
              recipient_list=[send_to_email],
              fail_silently=False
              )

def generate_otp():
    return str(random.randint(100000, 999999))

def generate_and_send_otp(user):
    otp_code = generate_otp()
    EmailVerification.objects.update_or_create(
        user=user,
        defaults={'otp': otp_code}
    )
    send_email(user.email, otp_code)