from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.utilities.pagination import StandardResultsSetPagination
from payments.models import PaymentAllocation
from payments.serializers.payment_allocation_serializer import PaymentAllocationSerializer
from payments.permissions.payment_permissions import PaymentsPermissions
from loguru import logger


class PaymentAllocationViewSet(ModelViewSet):
    """
    ViewSet for managing PaymentAllocations.
    Supports listing, retrieving, creating, updating, and deleting allocations.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = PaymentAllocation.objects.all()
    serializer_class = PaymentAllocationSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [PaymentsPermissions]

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'allocation_number',
        'company__name',
        'branch__name',
        'payment__payment_number'
    ]
    ordering_fields = ['created_at', 'updated_at', 'allocation_date', 'amount_allocated']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            return get_company_queryset(self.request, PaymentAllocation).select_related(
                'company', 'branch', 'payment'
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {e}"

    def perform_create(self, serializer):
        user = self.request.user
        company = get_logged_in_company(self.request)

        allocation = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.success(
            f"PaymentAllocation '{allocation.allocation_number}' created by '{actor}' "
            f"for company '{allocation.company.name}'."
        )

    def perform_update(self, serializer):
        user = self.request.user
        company = get_logged_in_company(self.request)

        allocation = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.info(
            f"PaymentAllocation '{allocation.allocation_number}' updated by '{actor}' "
            f"for company '{allocation.company.name}'."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = get_logged_in_company(self.request)

        allocation_number = instance.allocation_number
        instance.delete()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.warning(
            f"PaymentAllocation '{allocation_number}' deleted by '{actor}' "
            f"from company '{company.name}'."
        )
