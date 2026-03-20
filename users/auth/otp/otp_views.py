from datetime import timedelta
import secrets
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.auth.otp.otp_model import PasswordResetOTP
from users.auth.otp.password_reset_request_serializer import PasswordResetRequestSerializer
from users.auth.otp.password_confirm_serializer import PasswordResetConfirmSerializer
from users.throttling.password_request_throttling import PasswordResetRequestThrottle
from users.tasks import send_otp_email_task
from users.auth.otp.otp_service import OTPService
from django.conf import settings


User = get_user_model()





class PasswordResetRequestView(APIView):
    throttle_classes = [PasswordResetRequestThrottle]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            
            # Prevent email enumeration
            return Response(
                {"message": "If an account exists, an OTP has been sent."},
                status=status.HTTP_200_OK
            )

        # Generate 6-digit OTP
        otp = OTPService.generate_otp(user)

        # Send email
        send_otp_email_task.delay(email, otp)

        return Response(
            {"message": "If an account exists, an OTP has been sent."},
            status=status.HTTP_200_OK
        )



class PasswordResetConfirmView(APIView):

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp_input = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid OTP or email."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            otp_record = PasswordResetOTP.objects.get(
                user=user,
                otp=otp_input,
                is_used=False
            )
        except PasswordResetOTP.DoesNotExist:
            return Response(
                {"error": "Invalid OTP or email."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check expiration
        if otp_record.expires_at < timezone.now():
            return Response(
                {"error": "OTP has expired."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mark OTP as used
        otp_record.is_used = True
        otp_record.save()

        # Set new password
        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password reset successful."},
            status=status.HTTP_200_OK
        )