# users/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.conf import settings
from users.models.user_model import User
from users.serializers.user_serializer import UserSerializer
from users.serializers.user_auth_serializer import UserLoginSerializer
from users.permissions.user_permissions import UserPermissions
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.pagination.pagination import StandardResultsSetPagination
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from django.db.models import Q
from users.services.user_service import UserService
from loguru import logger

class UserViewSet(ModelViewSet):
    """
    Full CRUD + extra actions for User management.
    Includes: activate/deactivate, role management, password reset, bulk operations, and search.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('first_name', 'last_name', 'email', 'role')
    ordering_fields = '__all__'
    ordering = ['first_name']

    permission_classes = [UserPermissions]
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication]

    def get_queryset(self):
        current = self.request.user

        # Company admin can see all users in their company
        if isinstance(current, User) and current.is_staff:
            return User.objects.filter(company=current.company)

        # Regular users can only see themselves
        if isinstance(current, User):
            return User.objects.filter(id=current.id)

        # Fallback: no access
        return User.objects.none()

    # -------------------------
    # Single User Actions
    # -------------------------
    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        user = self.get_object()
        UserService.activate_user(user)
        return Response({"detail": f"User '{user.username}' activated."})

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        UserService.deactivate_user(user)
        return Response({"detail": f"User '{user.username}' deactivated."})

    @action(detail=True, methods=["post"])
    def assign_role(self, request, pk=None):
        user = self.get_object()
        role = request.data.get("role")
        if not role:
            return Response({"detail": "Role is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            UserService.assign_role_to_user(user, role)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": f"Role '{role}' assigned to user '{user.username}'."})

    @action(detail=True, methods=["post"])
    def remove_role(self, request, pk=None):
        user = self.get_object()
        UserService.remove_role_from_user(user)
        return Response({"detail": f"Role removed from user '{user.username}'."})

    @action(detail=True, methods=["post"])
    def reset_password(self, request, pk=None):
        user = self.get_object()
        new_password = request.data.get("new_password")
        if not new_password:
            return Response({"detail": "New password is required."}, status=status.HTTP_400_BAD_REQUEST)
        UserService.reset_user_password(user, new_password)
        return Response({"detail": f"Password reset for user '{user.username}'."})

    # -------------------------
    # Bulk Actions
    # -------------------------
    @action(detail=False, methods=["post"])
    def activate_bulk(self, request):
        ids = request.data.get("user_ids", [])
        if not ids:
            return Response({"detail": "No user IDs provided."}, status=status.HTTP_400_BAD_REQUEST)
        users = User.objects.filter(id__in=ids)
        UserService.activate_users(list(users))
        return Response({"detail": f"Activated {users.count()} users."})

    @action(detail=False, methods=["post"])
    def deactivate_bulk(self, request):
        ids = request.data.get("user_ids", [])
        if not ids:
            return Response({"detail": "No user IDs provided."}, status=status.HTTP_400_BAD_REQUEST)
        users = User.objects.filter(id__in=ids)
        UserService.deactivate_users(list(users))
        return Response({"detail": f"Deactivated {users.count()} users."})

    @action(detail=False, methods=["post"])
    def assign_role_bulk(self, request):
        ids = request.data.get("user_ids", [])
        role = request.data.get("role")
        if not ids or not role:
            return Response({"detail": "User IDs and role are required."}, status=status.HTTP_400_BAD_REQUEST)
        users = User.objects.filter(id__in=ids)
        try:
            UserService.assign_role_to_users(list(users), role)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": f"Assigned role '{role}' to {users.count()} users."})

    @action(detail=False, methods=["post"])
    def delete_bulk(self, request):
        ids = request.data.get("user_ids", [])
        if not ids:
            return Response({"detail": "No user IDs provided."}, status=status.HTTP_400_BAD_REQUEST)
        users = User.objects.filter(id__in=ids)
        count = users.count()
        users.delete()
        return Response({"detail": f"Deleted {count} users."})

    @action(detail=False, methods=["post"])
    def reset_password_bulk(self, request):
        ids = request.data.get("user_ids", [])
        new_password = request.data.get("new_password")
        if not ids or not new_password:
            return Response({"detail": "User IDs and new password are required."}, status=status.HTTP_400_BAD_REQUEST)
        users = User.objects.filter(id__in=ids)
        for user in users:
            UserService.reset_user_password(user, new_password)
        return Response({"detail": f"Password reset for {users.count()} users."})

    # -------------------------
    # Search / Query
    # -------------------------
    @action(detail=False, methods=["get"])
    def search(self, request):
        query = request.query_params.get("q", "")
        role = request.query_params.get("role", None)
        if not query and not role:
            return Response({"detail": "Provide a search query or role."}, status=status.HTTP_400_BAD_REQUEST)

        qs = User.objects.all()
        if query:
            qs = qs.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query))
        if role:
            if role not in UserService.ALLOWED_ROLES:
                return Response({"detail": f"Role '{role}' is invalid."}, status=status.HTTP_400_BAD_REQUEST)
            qs = qs.filter(role=role)

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)




# Register a new user (by company admin)
class UserRegisterView(APIView):
    permission_classes = [UserPermissions]
    authentication_classes = [CompanyCookieJWTAuthentication]

    @swagger_auto_schema(request_body=UserSerializer)
    def post(self, request):
        #Taking care of the 2 different possibilities that either user creating or regestering user might be company or user .
        #If user is creating user then request.user.company works to assign company but if company is creating user then request.user.company does not work
        try:
            #Get user branch and company
            logger.info({
                "request":request.data,
                "user": request.user
            })
            serializer = UserSerializer(data=request.data)
            if not serializer.is_valid():
                print(serializer.errors)  # <- This will show what is failing
            serializer.is_valid(raise_exception=True)
            serializer.save(company = self.request.user.company, branch = request.user.branch)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.info({
                "request":request.data,
                "user": request.user
            })
            serializer = UserSerializer(data=request.data)
            if not serializer.is_valid():
                print(serializer.errors)  # <- This will show what is failing
            serializer.is_valid(raise_exception=True)
            serializer.save(company = self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)



# Update an existing user
class UserUpdateView(APIView):
    permission_classes = [UserPermissions]

    @swagger_auto_schema(request_body=UserSerializer)
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
    permission_classes = [UserPermissions]

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

    @swagger_auto_schema(request_body=UserSerializer)
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

