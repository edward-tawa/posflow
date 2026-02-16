from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from loguru import logger
from django.db.models import Q
from employees.models.employee_budget_model import EmployeeBudget
from employees.serializers.employee_budget_serializer import EmployeeBudgetSerializer
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from employees.permissions.employee_permissions import EmployeePermission
from rest_framework.filters import SearchFilter, OrderingFilter
from config.pagination.pagination import StandardResultsSetPagination
from company.models.company_model import Company



class EmployeeBudgetViewSet(ModelViewSet):
    """
    ViewSet for viewing and managing employee budgets.
    Supports listing, retrieving, creating, updating, and deleting budgets.
    Includes detailed logging for key operations.
    """
    queryset = EmployeeBudget.objects.all()
    serializer_class = EmployeeBudgetSerializer
    authentication_classes = [CompanyCookieJWTAuthentication, UserCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [EmployeePermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'employee__first_name', 'employee__last_name',
        'branch__name', 'company__name'
    ]
    ordering_fields = [
        'salary', 'bonus', 'commission', 'overtime', 'allowance',
        'other', 'deductions', 'paid', 'created_at', 'updated_at'
    ]
    ordering = ['employee__first_name', 'employee__last_name']
    pagination_class = StandardResultsSetPagination

    # -------------------------
    # QUERYSET FILTERING
    # -------------------------
    def get_queryset(self):
        try:
            user = self.request.user
            if not user.is_authenticated:
                logger.warning("Unauthenticated access attempt to EmployeeBudgetViewSet.")
                return EmployeeBudget.objects.none()

            # Determine the "company context"
            company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
            identifier = getattr(company, 'name', None) or getattr(company, 'username', None) or 'Unknown'

            if not company:
                logger.warning(f"{identifier} has no associated company.")
                return EmployeeBudget.objects.none()

            logger.info(f"{identifier} fetching employee budgets for company '{getattr(company, 'name', 'Unknown')}'.")
            return EmployeeBudget.objects.filter(company=company).select_related('employee', 'branch', 'company', 'user')
        except Exception as e:
            logger.error(e)
            return self.queryset.none()

    # -------------------------
    # CREATE
    # -------------------------
    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        budget = serializer.save(company=company, branch=user.branch, created_by=user, updated_by=user)
        identifier = getattr(user, 'username', None) or getattr(company, 'name', 'Unknown')
        logger.success(
            f"EmployeeBudget for '{budget.employee}' created by {identifier} in company '{getattr(company, 'name', 'Unknown')}'."
        )

    # -------------------------
    # UPDATE
    # -------------------------
    def perform_update(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        budget = serializer.save(updated_by=user)
        identifier = getattr(user, 'username', None) or getattr(company, 'name', 'Unknown')
        logger.info(f"EmployeeBudget for '{budget.employee}' updated by {identifier}.")

    # -------------------------
    # DELETE
    # -------------------------
    def perform_destroy(self, instance):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        identifier = getattr(user, 'username', None) or getattr(company, 'name', 'Unknown')
        logger.warning(f"EmployeeBudget for '{instance.employee}' deleted by {identifier}.")
        instance.delete()
