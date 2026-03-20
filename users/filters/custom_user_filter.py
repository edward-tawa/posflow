from django_filters import FilterSet
from users.models.user_model import User


class CustomUserFilter(FilterSet):
    class Meta:
        model = User

        fields = {
            'email': ['exact', 'icontains'],
            'first_name': ['exact', 'icontains'],
            'last_name': ['exact', 'icontains'],
            'is_active': ['exact'],
            'username': ['exact', 'icontains'],
        }