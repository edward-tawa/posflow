from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from employees.models.remuneration_model import Remuneration
from employees.serializers.remuneration_serializer import RemunerationSerializer
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from employees.permissions.employee_permissions import EmployeePermission
from config.pagination.pagination import StandardResultsSetPagination
from company.models.company_model import Company
from loguru import logger
from django.db.models import Q


class RemunerationViewSet(ModelViewSet):
    """
    ViewSet for viewing and managing remunerations.
    Supports listing, retrieving, creating, updating, and deleting remunerations.
    Includes detailed logging for key operations.
    """
    queryset = Remuneration.objects.all()
    serializer_class = RemunerationSerializer
    authentication_classes = [CompanyCookieJWTAuthentication, UserCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [EmployeePermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'employee__first_name', 'employee__last_name', 'employee__email',
        'type', 'amount'
    ]
    ordering_fields = [
        'employee__first_name', 'employee__last_name', 'employee__email',
        'type', 'amount', 'effective_date', 'created_at'
    ]
    ordering = ['-effective_date', '-created_at']
    pagination_class = StandardResultsSetPagination

    # -------------------------
    # QUERYSET FILTERING
    # -------------------------
    def get_queryset(self):
        try:
            user = self.request.user
            if not user.is_authenticated:
                logger.warning("Unauthenticated access attempt to RemunerationViewSet.")
                return Remuneration.objects.none()

            # Determine the company context
            company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
            identifier = getattr(company, 'name', None) or getattr(user, 'username', None) or 'Unknown'

            if not company:
                logger.warning(f"{identifier} has no associated company.")
                return Remuneration.objects.none()

            logger.info(f"{identifier} fetching remunerations for company '{getattr(company, 'name', 'Unknown')}'.")
            return Remuneration.objects.filter(company=company).select_related('employee', 'branch', 'company', 'user')
        except Exception as e:
            logger.error(e)
            return self.queryset.none()

    # -------------------------
    # CREATE
    # -------------------------
    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)

        remuneration = serializer.save(
            company=company,
            branch=getattr(user, 'branch', None),
            created_by=user,
            updated_by=user
        )

        identifier = getattr(user, 'username', None) or getattr(company, 'name', 'Unknown')
        logger.success(
            f"Remuneration '{remuneration.id}' ({remuneration.type} - {remuneration.amount}) "
            f"created for employee '{remuneration.employee.id}' by {identifier}."
        )

    # -------------------------
    # UPDATE
    # -------------------------
    def perform_update(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)

        remuneration = serializer.save(updated_by=user)
        identifier = getattr(user, 'username', None) or getattr(company, 'name', 'Unknown')

        logger.info(
            f"Remuneration '{remuneration.id}' ({remuneration.type} - {remuneration.amount}) "
            f"updated by {identifier}."
        )

    # -------------------------
    # DELETE
    # -------------------------
    def perform_destroy(self, instance):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        identifier = getattr(user, 'username', None) or getattr(company, 'name', 'Unknown')

        logger.warning(
            f"Remuneration '{instance.id}' ({instance.type} - {instance.amount}) "
            f"deleted by {identifier}."
        )
        instance.delete()
