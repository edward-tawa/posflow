# users/auth/services/otp_service.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_otp_email_task(user_email, otp):
    send_mail(
        subject="Your Password Reset OTP",
        message=f"Your OTP is {otp}. It expires in 10 minutes.",
        from_email=settings.DEFAULT_FROM_EMAIL,  # uses default from settings
        recipient_list=[user_email],
    )