import secrets

from django.db import models
from time import timezone
import uuid

class PasswordResetOTP(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    otp = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)




   



    def __str__(self):
        return f"OTP for {self.user.email} - Expires at: {self.expires_at} - Used: {self.is_used}"
