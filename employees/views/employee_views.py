from rest_framework.viewsets import ModelViewSet
from employees.models.employee_model import Employee
from employees.serializers.employee_serializer import EmployeeSerializer
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from employees.permissions.employee_permissions import EmployeePermission
from rest_framework.filters import SearchFilter, OrderingFilter
from config.pagination.pagination import StandardResultsSetPagination
from company.models.company_model import Company
from loguru import logger
from django.db.models import Q


class EmployeeViewSet(ModelViewSet):
    """
    ViewSet for viewing and managing employees.
    Supports listing, retrieving, creating, updating, and deleting employees.
    Includes detailed logging for key operations.
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    authentication_classes = [CompanyCookieJWTAuthentication, UserCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [EmployeePermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'first_name', 'last_name', 'email', 'phone_number',
        'department', 'position', 'grade', 'status'
    ]
    ordering_fields = [
        'first_name', 'last_name', 'email', 'department',
        'position', 'grade', 'status', 'created_at'
    ]
    ordering = ['first_name', 'last_name']
    pagination_class = StandardResultsSetPagination

    # -------------------------
    # QUERYSET FILTERING
    # -------------------------
    def get_queryset(self):
        try:
            user = self.request.user
            if not user.is_authenticated:
                logger.warning("Unauthenticated access attempt to EmployeeViewSet.")
                return Employee.objects.none()

            # Determine the "company context"
            company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
            identifier = getattr(company, 'name', None) or getattr(company, 'username', None) or 'Unknown'

            if not company:
                logger.warning(f"{identifier} has no associated company.")
                return Employee.objects.none()

            logger.info(f"{identifier} fetching employees for company '{getattr(company, 'name', 'Unknown')}'.")
            return Employee.objects.filter(company=company).select_related('branch', 'company', 'user')
        except Exception as e:
            logger.error(e)
            return self.queryset.none()

    # -------------------------
    # CREATE
    # -------------------------
    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        employee = serializer.save(company=company, branch=user.branch, created_by=user, updated_by=user)
        identifier = getattr(user, 'username', None) or getattr(company, 'name', 'Unknown')
        logger.success(
            f"Employee '{employee.full_name}' ({employee.employee_number}) created "
            f"by {identifier} in company '{getattr(company, 'name', 'Unknown')}'."
        )

    # -------------------------
    # UPDATE
    # -------------------------
    def perform_update(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        employee = serializer.save(updated_by=user)
        identifier = getattr(user, 'username', None) or getattr(company, 'name', 'Unknown')
        logger.info(f"Employee '{employee.full_name}' ({employee.employee_number}) updated by {identifier}.")

    # -------------------------
    # DELETE
    # -------------------------
    def perform_destroy(self, instance):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        identifier = getattr(user, 'username', None) or getattr(company, 'name', 'Unknown')
        logger.warning(f"Employee '{instance.full_name}' ({instance.employee_number}) deleted by {identifier}.")
        instance.delete()
