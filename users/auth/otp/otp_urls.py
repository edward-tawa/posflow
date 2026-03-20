from django.urls import path
from users.auth.otp.otp_views import PasswordResetConfirmView, PasswordResetRequestView


urlpatterns = [
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]