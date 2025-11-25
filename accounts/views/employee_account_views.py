from rest_framework.viewsets import ModelViewSet
from accounts.models.employee_account_model import EmployeeAccount
from accounts.serializers.employee_account_serializer import EmployeeAccountSerializer
from rest_framework.permissions import IsAuthenticated
from config.auth.jwt_token_authentication import UserCookieJWTAuthentication, CompanyCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from config.utilities.pagination import StandardResultsSetPagination
from config.utilities.get_queryset import get_company_queryset
from accounts.permissions.account_permissions import AccountPermission
from company.models.company_model import Company
from loguru import logger


class EmployeeAccountViewSet(ModelViewSet):
    """
    ViewSet for managing Employee Accounts within a company.
    Provides CRUD operations with appropriate permissions and filtering.
    """
    queryset = EmployeeAccount.objects.all()
    serializer_class = EmployeeAccountSerializer
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [AccountPermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['employee__name', 'account__name', 'account__number']
    ordering_fields = ['created_at', 'updated_at', 'employee__name']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Return EmployeeAccount queryset filtered by the logged-in company/user."""
        return get_company_queryset(self.request, EmployeeAccount).select_related('employee', 'account')
    
    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        employee_account = serializer.save(company=company)
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(employee=employee_account.employee.name, account_number=employee_account.account.number).success(
            f"EmployeeAccount for employee '{employee_account.employee.name}' and account '{employee_account.account.name}' (Number: {employee_account.account.number}) created by {actor} in company '{getattr(company, 'name', 'Unknown')}'."
        )
    
    def perform_update(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        employee_account = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(employee=employee_account.employee.name, account_number=employee_account.account.number).info(
            f"EmployeeAccount for employee '{employee_account.employee.name}' and account '{employee_account.account.name}' (Number: {employee_account.account.number}) updated by {actor}."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(employee=instance.employee.name, account_number=instance.account.number).warning(
            f"EmployeeAccount for employee '{instance.employee.name}' and account '{instance.account.name}' (Number: {instance.account.number}) deleted by {actor}."
        )
        instance.delete()