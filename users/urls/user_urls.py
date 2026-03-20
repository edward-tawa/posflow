# users/urls.py
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from users.auth.otp.otp_views import PasswordResetConfirmView, PasswordResetRequestView
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
    path('user/password-reset/request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('user/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    # Include read-only router endpoints
    path('', include(router.urls)),
]
