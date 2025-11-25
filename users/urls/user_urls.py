# users/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from users.views.user_views import (
    UserViewSet,
    UserLoginView,
    UserLogoutView,
    UserRegisterView,
    UserUpdateView,
    UserDeleteView,
    UserTokenRefreshView
)

# Router for read-only user list/retrieve
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # Auth and CRUD endpoints
    path('user/login/', UserLoginView.as_view(), name='user-login'),
    path('user/logout/', UserLogoutView.as_view(), name='user-logout'),
    path('user/register/', UserRegisterView.as_view(), name='user-register'),
    path('user/token/refresh/', UserTokenRefreshView.as_view(), name='user-token-refresh'),
    path('user/<int:pk>/update/', UserUpdateView.as_view(), name='user-update'),
    path('user/<int:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),

    # Include read-only router endpoints
    path('', include(router.urls)),
]
