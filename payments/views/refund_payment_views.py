from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from payments.models.refund_payment_model import RefundPayment
from payments.serializers.refund_payment_serializer import RefundPaymentSerializer
from payments.permissions.payment_permissions import PaymentsPermissions
from loguru import logger


class RefundPaymentViewSet(ModelViewSet):
    """
    ViewSet for managing RefundPayments.
    Supports listing, retrieving, creating, updating, and deleting refund payments.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = RefundPayment.objects.all()
    serializer_class = RefundPaymentSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [PaymentsPermissions]

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'id',
        'company__name',
        'branch__name',
        'refund__refund_number',
        'payment__reference_number'
    ]
    ordering_fields = ['created_at', 'updated_at', 'id']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            return get_company_queryset(self.request, RefundPayment).select_related(
                'company', 'branch', 'refund', 'payment', 'processed_by'
            )
        except Exception as e:
            logger.error(f"Error fetching RefundPayment queryset: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        company = get_logged_in_company(self.request)

        refund_payment = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.success(
            f"RefundPayment '{refund_payment.id}' created by '{actor}' "
            f"for company '{refund_payment.company.name}'."
        )

    def perform_update(self, serializer):
        user = self.request.user
        company = get_logged_in_company(self.request)

        refund_payment = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.info(
            f"RefundPayment '{refund_payment.id}' updated by '{actor}' "
            f"for company '{refund_payment.company.name}'."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = get_logged_in_company(self.request)

        payment_id = instance.id
        instance.delete()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.warning(
            f"RefundPayment '{payment_id}' deleted by '{actor}' "
            f"from company '{company.name}'."
        )
