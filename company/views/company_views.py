from rest_framework import status
from django.conf import settings
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication
from company.models.company_model import Company
from company.serializers.company_serializer import CompanySerializer
from company.serializers.company_auth_serializer import CompanyLoginSerializer
from company.permissions.company_create_or_is_admin import CompanyCreateOrAdminPermission
from config.utilities.pagination import StandardResultsSetPagination
from loguru import logger
from config.utilities.check_company_existance import check_existance


# Only list and retrieve companies via this ViewSet
class CompanyViewSet(ReadOnlyModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('name', 'email')
    ordering_fields = '__all__'
    ordering = ['name']

    permission_classes = [CompanyCreateOrAdminPermission]
    authentication_classes = [CompanyCookieJWTAuthentication, JWTAuthentication]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Company.objects.all()
        elif user.is_staff:
            return Company.objects.filter(id=user.company.id)
        else:
            return Company.objects.none()


# Register a new company
class CompanyRegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def post(self, request):
        exist = check_existance(company_data=request.data)
        if not exist:
            serializer = CompanySerializer(data=request.data)
            company_name = request.data.get('name')
            serializer.is_valid(raise_exception=True)
            serializer.save()
            logger.info(f"{company_name} successfully registered")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {
                'Company': request.data.get('name'),
                'Email': request.data.get('email'),
                'Phone': request.data.get('phone_number'),
                'Message': 'Company with the above information already exists'
            },
            status.HTTP_406_NOT_ACCEPTABLE
        )
        


# Update an existing company
class CompanyUpdateView(APIView):
    permission_classes = [CompanyCreateOrAdminPermission]
    def patch(self, request, pk):
        company = Company.objects.get(pk=pk)
        serializer = CompanySerializer(company, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# Delete an existing company
class CompanyDeleteView(APIView):
    permission_classes = [CompanyCreateOrAdminPermission]
    def delete(self, request, pk):
        try:
            company = Company.objects.get(pk=pk)
        except Company.DoesNotExist:
            return Response({"error": "Company not found."}, status=status.HTTP_404_NOT_FOUND)

        company.delete()
        return Response({"message": "Company deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# Company login
class CompanyLoginView(APIView):
    permission_classes = [CompanyCreateOrAdminPermission]

    def post(self, request):
        serializer = CompanyLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        company = authenticate(request, email=email, password=password)
        if company is None:
            return Response({"error": "Invalid email or password."}, status=401)

        if not company.is_active:
            return Response({"error": "This account is inactive."}, status=403)

        # Generate tokens
        refresh = RefreshToken.for_user(company)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Create response
        response = Response({"message": "Login successful"}, status=200)

        # Development vs production cookie flags
        secure_flag = not settings.DEBUG  # True if production, False if dev

        # Set company cookies (matching authentication class)
        response.set_cookie(
            key="company_access_token",
            value=access_token,
            httponly=True,
            secure=secure_flag,
            samesite="Lax",
            max_age=60 * 60 * 24  # 1 day
        )
        response.set_cookie(
            key="company_refresh_token",
            value=refresh_token,
            httponly=True,
            secure=secure_flag,
            samesite="Lax",
            max_age=60 * 60 * 24 * 7  # 7 days
        )

        return response

    

class CompanyLogoutView(APIView):
    """
    Logs out the company by clearing JWT cookies.
    """
    authentication_classes = [CompanyCookieJWTAuthentication, JWTAuthentication]
    def post(self, request):
        response = Response({"message": "Logout successful"}, status=status.HTTP_200_OK)

        # Delete cookies
        response.delete_cookie("company_access_token")
        response.delete_cookie("company_refresh_token")

        return response



class CompanyTokenRefreshView(APIView):
    """
    Refreshes the company access token using the refresh token from cookies.
    """
    authentication_classes = []  # No auth required
    permission_classes = []      # Anyone with a valid refresh token can access

    def post(self, request):
        refresh_token = request.COOKIES.get("company_refresh_token")
        if not refresh_token:
            return Response({"error": "Refresh token not found."}, status=401)

        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)

            # Optionally rotate refresh tokens:
            # refresh.blacklist()  # if using blacklist app
            # new_refresh_token = str(refresh)

            secure_flag = not settings.DEBUG
            response = Response(
                {"message": "Token refreshed", "access": new_access_token}, 
                status=200
            )

            # Update cookie with new access token
            response.set_cookie(
                key="company_access_token",
                value=new_access_token,
                httponly=True,
                secure=secure_flag,
                samesite="Lax",
                max_age=60 * 60 * 24  # 1 day
            )

            return response

        except TokenError:
            return Response({"error": "Invalid or expired refresh token."}, status=401)