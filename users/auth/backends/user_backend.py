from django.contrib.auth.backends import ModelBackend
from users.models.user_model import User

class UserBackend(ModelBackend):
    def authenticate(self, request, username=None, email=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=email) or User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
