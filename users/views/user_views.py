# users/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.conf import settings
from users.models.user_model import User
from users.serializers.user_serializer import UserSerializer
from users.serializers.user_auth_serializer import UserLoginSerializer
from users.permissions.user_management_permission import CompanyAdminOrSuperuserCanManageUsers
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.pagination import StandardResultsSetPagination
from rest_framework.permissions import AllowAny

# Read-only ViewSet for listing/retrieving users
class UserViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('first_name', 'email', 'role')
    ordering_fields = '__all__'
    ordering = ['first_name']

    permission_classes = [CompanyAdminOrSuperuserCanManageUsers]
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication]

    def get_queryset(self):
        current = self.request.user

        # If a regular User instance
        if isinstance(current, User):
            if current.is_staff:
                # Company admin can see all users in their company
                return User.objects.filter(company=current.company)
            return User.objects.filter(id=current.id)  # Regular user can only see themselves

        # If a Company instance (superuser), can see all users of that company
        elif hasattr(current, "id"):  # crude check for Company
            return User.objects.filter(company=current)

        return User.objects.none()




# Register a new user (by company admin)
class UserRegisterView(APIView):
    permission_classes = [CompanyAdminOrSuperuserCanManageUsers]
    authentication_classes = [CompanyCookieJWTAuthentication]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)  # <- This will show what is failing
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Update an existing user
class UserUpdateView(APIView):
    permission_classes = [CompanyAdminOrSuperuserCanManageUsers]

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# Delete an existing user
class UserDeleteView(APIView):
    permission_classes = [CompanyAdminOrSuperuserCanManageUsers]

    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        user.delete()
        return Response({"message": "User deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# Optional: User login
class UserLoginView(APIView):
    permission_classes = [AllowAny] 
    serializer_class = UserLoginSerializer
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response({"error": "Invalid email or password."}, status=401)

        if not user.is_active:
            return Response({"error": "This account is inactive."}, status=403)

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Create response
        response = Response(
            {
                "message": "Login successful",
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user_data': serializer.data
            }, 
            status=200
        )

        # Development vs production cookie flags
        secure_flag = not settings.DEBUG  # True if production, False if development

        # Set user cookies (matching authentication class)
        response.set_cookie(
            key="user_access_token",
            value=access_token,
            httponly=True,
            secure=secure_flag,
            samesite="Lax",
            max_age=60 * 60 * 24  # 1 day
        )
        response.set_cookie(
            key="user_refresh_token",
            value=refresh_token,
            httponly=True,
            secure=secure_flag,
            samesite="Lax",
            max_age=60 * 60 * 24 * 7  # 7 days
        )

        return response
    

class UserLogoutView(APIView):
    """
    Logs out the user by clearing the access and refresh tokens from cookies.
    """
    def post(self, request):
        response = Response({"message": "Logout successful"}, status=status.HTTP_200_OK)

        # Clear cookies by setting empty value and max_age=0
        response.delete_cookie("user_access_token")
        response.delete_cookie("user_refresh_token")
        
        return response
    


class UserTokenRefreshView(APIView):
    """
    Refreshes the access token using the refresh token from cookies.
    """
    authentication_classes = []  # No auth required
    permission_classes = []      # Anyone with a valid refresh token can access

    def post(self, request):
        refresh_token = request.COOKIES.get("user_refresh_token")
        if not refresh_token:
            return Response({"error": "Refresh token not found."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)

            # Optionally, you can rotate refresh tokens if you want:
            # refresh = refresh.rotate()
            # new_refresh_token = str(refresh)

            secure_flag = not settings.DEBUG
            response = Response(
                {
                    "message": "Token refreshed", 
                    "access": new_access_token
                }, 
                status=200
            )

            # Update cookie with new access token
            response.set_cookie(
                key="user_access_token",
                value=new_access_token,
                httponly=True,
                secure=secure_flag,
                samesite="Lax",
                max_age=60 * 60 * 24  # 1 day
            )

            return response

        except TokenError:
            return Response({"error": "Invalid or expired refresh token."}, status=status.HTTP_401_UNAUTHORIZED)

