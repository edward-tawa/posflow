from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from payments.models.refund_model import Refund
from payments.serializers.refund_serializer import RefundSerializer
from payments.permissions.payment_permissions import PaymentsPermissions
from loguru import logger


class RefundViewSet(ModelViewSet):
    """
    ViewSet for managing Refunds.
    Supports listing, retrieving, creating, updating, and deleting refunds.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = Refund.objects.all()
    serializer_class = RefundSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [PaymentsPermissions]

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'refund_number',
        'company__name',
        'branch__name',
        'payment__payment_number',
        'processed_by__name',
        'reason',
        'notes'
    ]
    ordering_fields = ['created_at', 'updated_at', 'refund_date', 'amount']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            return get_company_queryset(self.request, Refund).select_related(
                'company', 'branch', 'payment', 'processed_by'
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {e}"

    def perform_create(self, serializer):
        user = self.request.user
        company = get_logged_in_company(self.request)

        refund = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.success(
            f"Refund '{refund.refund_number}' created by '{actor}' "
            f"for company '{refund.company.name}'."
        )

    def perform_update(self, serializer):
        user = self.request.user
        company = get_logged_in_company(self.request)

        refund = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.info(
            f"Refund '{refund.refund_number}' updated by '{actor}' "
            f"for company '{refund.company.name}'."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = get_logged_in_company(self.request)

        refund_number = instance.refund_number
        instance.delete()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.warning(
            f"Refund '{refund_number}' deleted by '{actor}' "
            f"from company '{company.name}'."
        )
