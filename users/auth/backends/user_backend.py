from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from users.models.user_model import User

class UserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(
                Q(username=username) | Q(email=username)
            )

        except User.DoesNotExist:
            return None
        
        if user.check_password(password):
            return user
        
        return None
        
            