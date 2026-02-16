from rest_framework.viewsets import ModelViewSet
from employees.models.employee_contract_model import EmployeeContract
from employees.serializers.employee_contract_serializer import EmployeeContractSerializer
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from employees.permissions.employee_permissions import EmployeePermission
from rest_framework.filters import SearchFilter, OrderingFilter
from config.pagination.pagination import StandardResultsSetPagination
from employees.models.employee_model import Employee
from loguru import logger
from django.db.models import Q


class EmployeeContractViewSet(ModelViewSet):
    """
    ViewSet for viewing and managing employee contracts.
    Supports listing, retrieving, creating, updating, and deleting contracts.
    Includes detailed logging for key operations.
    """
    queryset = EmployeeContract.objects.all()
    serializer_class = EmployeeContractSerializer
    authentication_classes = [CompanyCookieJWTAuthentication, UserCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [EmployeePermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'employee__first_name', 'employee__last_name', 'employee__email',
        'contract_type', 'terms'
    ]
    ordering_fields = [
        'start_date', 'end_date', 'contract_type', 'created_at'
    ]
    ordering = ['start_date']
    pagination_class = StandardResultsSetPagination

    # -------------------------
    # QUERYSET FILTERING
    # -------------------------
    def get_queryset(self):
        try:
            user = self.request.user
            if not user.is_authenticated:
                logger.warning("Unauthenticated access attempt to EmployeeContractViewSet.")
                return EmployeeContract.objects.none()

            # Determine the "company context"
            company = getattr(user, 'company', None)
            identifier = getattr(user, 'username', None) or getattr(company, 'name', 'Unknown')

            if not company:
                logger.warning(f"{identifier} has no associated company.")
                return EmployeeContract.objects.none()

            logger.info(f"{identifier} fetching contracts for company '{getattr(company, 'name', 'Unknown')}'.")
            return EmployeeContract.objects.filter(employee__company=company).select_related('employee', 'user')
        except Exception as e:
            logger.error(e)
            return self.queryset.none()

    # -------------------------
    # CREATE
    # -------------------------
    def perform_create(self, serializer):
        user = self.request.user
        contract = serializer.save(created_by=user, updated_by=user)
        identifier = getattr(user, 'username', None)
        logger.success(
            f"EmployeeContract '{contract.id}' for employee '{contract.employee.full_name}' "
            f"created by {identifier}."
        )

    # -------------------------
    # UPDATE
    # -------------------------
    def perform_update(self, serializer):
        user = self.request.user
        contract = serializer.save(updated_by=user)
        identifier = getattr(user, 'username', None)
        logger.info(
            f"EmployeeContract '{contract.id}' for employee '{contract.employee.full_name}' updated by {identifier}."
        )

    # -------------------------
    # DELETE
    # -------------------------
    def perform_destroy(self, instance):
        user = self.request.user
        identifier = getattr(user, 'username', None)
        logger.warning(
            f"EmployeeContract '{instance.id}' for employee '{instance.employee.full_name}' deleted by {identifier}."
        )
        instance.delete()
