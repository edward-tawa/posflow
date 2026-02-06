from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from payments.models.purchase_payment_model import PurchasePayment
from payments.serializers.purchase_payment_serializer import PurchasePaymentSerializer
from payments.permissions.payment_permissions import PaymentsPermissions
from loguru import logger


class PurchasePaymentViewSet(ModelViewSet):
    """
    ViewSet for managing PurchasePayments.
    Supports listing, retrieving, creating, updating, and deleting purchase payments.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = PurchasePayment.objects.all()
    serializer_class = PurchasePaymentSerializer
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
        'purchase_order__order_number',
        'purchase__reference_number',
        'purchase_invoice__invoice_number',
        'payment__reference_number'
    ]
    ordering_fields = ['created_at', 'updated_at', 'id']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            return get_company_queryset(self.request, PurchasePayment).select_related(
                'company', 'branch', 'purchase_order', 'purchase', 'purchase_invoice', 'payment', 'issued_by'
            )
        except Exception as e:
            logger.error(f"Error fetching PurchasePayment queryset: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        company = get_logged_in_company(self.request)

        purchase_payment = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.success(
            f"PurchasePayment '{purchase_payment.id}' created by '{actor}' "
            f"for company '{purchase_payment.company.name}'."
        )

    def perform_update(self, serializer):
        user = self.request.user
        company = get_logged_in_company(self.request)

        purchase_payment = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.info(
            f"PurchasePayment '{purchase_payment.id}' updated by '{actor}' "
            f"for company '{purchase_payment.company.name}'."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = get_logged_in_company(self.request)

        payment_id = instance.id
        instance.delete()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.warning(
            f"PurchasePayment '{payment_id}' deleted by '{actor}' "
            f"from company '{company.name}'."
        )
