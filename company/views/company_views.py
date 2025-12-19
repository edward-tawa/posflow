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
from config.pagination.pagination import StandardResultsSetPagination
from loguru import logger
from config.utilities.check_company_existance import check_existance
from company.services.company_service import CompanyService
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema


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
        
    


    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        company = self.get_object()
        CompanyService.activate_company(company)
        return Response({"detail": "Company activated."})

    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate(self, request, pk=None):
        company = self.get_object()
        CompanyService.deactivate_company(company)
        return Response({"detail": "Company deactivated."})

    # -------------------------
    # LOGO MANAGEMENT
    # -------------------------
    @action(detail=True, methods=["post"], url_path="set-logo")
    def set_logo(self, request, pk=None):
        company = self.get_object()
        logo_path = request.data.get("logo")

        if not logo_path:
            return Response(
                {"detail": "Logo path is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        CompanyService.set_company_logo(company, logo_path)
        return Response({"detail": "Company logo updated."})

    @action(detail=True, methods=["post"], url_path="remove-logo")
    def remove_logo(self, request, pk=None):
        company = self.get_object()
        CompanyService.remove_company_logo(company)
        return Response({"detail": "Company logo removed."})

    @action(detail=True, methods=["get"], url_path="logo")
    def get_logo(self, request, pk=None):
        company = self.get_object()
        return Response({"logo": company.logo})

    # -------------------------
    # LIST / FILTER
    # -------------------------
    @action(detail=False, methods=["get"], url_path="active")
    def active_companies(self, request):
        companies = CompanyService.list_active_companies()
        serializer = self.get_serializer(companies, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        query = request.query_params.get("q", "")
        companies = CompanyService.search_companies_by_name(query)
        serializer = self.get_serializer(companies, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="by-email-domain")
    def by_email_domain(self, request):
        domain = request.query_params.get("domain")
        if not domain:
            return Response(
                {"detail": "domain query param is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        companies = CompanyService.get_companies_by_email_domain(domain)
        serializer = self.get_serializer(companies, many=True)
        return Response(serializer.data)

    # -------------------------
    # STATS / UTILITIES
    # -------------------------
    @action(detail=False, methods=["get"], url_path="count")
    def count(self, request):
        return Response({"count": CompanyService.count_companies()})

    @action(detail=False, methods=["get"], url_path="count-active")
    def count_active(self, request):
        return Response({"count": CompanyService.count_active_companies()})

    @action(detail=False, methods=["get"], url_path="exists")
    def exists(self, request):
        name = request.query_params.get("name")
        if not name:
            return Response(
                {"detail": "name query param is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({"exists": CompanyService.company_exists(name)})


# Register a new company
class CompanyRegisterView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(request_body=CompanySerializer)
    def post(self, request):
       
        serializer = CompanySerializer(data=request.data)
        company_name = request.data.get('name')
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f"{company_name} company successfully registered")
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Update an existing company
class CompanyUpdateView(APIView):
    permission_classes = [CompanyCreateOrAdminPermission]
    @swagger_auto_schema(request_body=CompanySerializer)
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

    @swagger_auto_schema(request_body=CompanySerializer)
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
        response = Response(
            {
                "message": "Login successful",
                "access_token": access_token
            }, 
            status=200
        )

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