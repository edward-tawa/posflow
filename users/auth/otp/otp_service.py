from django.db import transaction as db_transaction
from loguru import logger
from users.auth.otp.otp_model import PasswordResetOTP
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
import secrets
from django.utils import timezone
from datetime import timedelta



class OTPService:

    MAX_ATTEMPTS = 5

    @staticmethod
    def generate_otp(user):
        otp_code = OTPService._generate_otp_number()

        hashed_otp = make_password(otp_code)
        expires_at = timezone.now() + timedelta(minutes=10)  # OTP valid for 10 minutes

        with db_transaction.atomic():
            # Invalidate any existing OTPs for the user
            PasswordResetOTP.objects.filter(user=user, is_used=False).update(is_used=True)


            # Create a new OTP entry
            otp_entry = PasswordResetOTP.objects.create(
                user=user,
                otp=hashed_otp,
                expires_at=expires_at
            )

        logger.info(f"Generated OTP for user {user.email})")
        return otp_code
    
    @staticmethod
    def _generate_otp_number():
        return ''.join(secrets.choice("0123456789") for _ in range(6))
    

    @staticmethod
    def validate_otp(user, otp_code):
        try:
            otp_entry = PasswordResetOTP.objects.filter(user=user, is_used=False).latest('expires_at')
        except PasswordResetOTP.DoesNotExist:
            return False, "No OTP found for this user."

        # Expiry check
        if otp_entry.expires_at < timezone.now():
            otp_entry.is_used = True
            otp_entry.save()
            return False, "OTP has expired."

        # Check OTP
        if not check_password(otp_code, otp_entry.otp):
            otp_entry.attempts += 1
            if otp_entry.attempts >= OTPService.MAX_ATTEMPTS:
                otp_entry.is_used = True
            otp_entry.save()
            return False, "Invalid OTP."


        # Valid OTP
        otp_entry.is_used = True
        otp_entry.save()
        return True, "OTP is valid."