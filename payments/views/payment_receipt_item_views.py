from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from payments.models.payment_receipt_item_model import PaymentReceiptItem
from payments.serializers.payment_receipt_item_serializer import PaymentReceiptItemSerializer
from payments.permissions.payment_permissions import PaymentsPermissions
from loguru import logger


class PaymentReceiptItemViewSet(ModelViewSet):
    """
    ViewSet for managing PaymentReceiptItems.
    Supports listing, retrieving, creating, updating, and deleting items.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = PaymentReceiptItem.objects.all()
    serializer_class = PaymentReceiptItemSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [PaymentsPermissions]

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'description',
        'payment_receipt__receipt_number',
        'payment_receipt__company__name',
        'payment_receipt__branch__name'
    ]
    ordering_fields = ['created_at', 'updated_at', 'quantity', 'unit_price', 'tax_rate', 'total_price']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            return (
                get_company_queryset(self.request, PaymentReceiptItem)
                .select_related('payment_receipt', 'payment_receipt__company', 'payment_receipt__branch')
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {e}"

    def perform_create(self, serializer):
        user = self.request.user
        company = get_logged_in_company(self.request)

        item = serializer.save()
        # Update receipt amount after creating item
        item.payment_receipt.update_amount_received()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.success(
            f"PaymentReceiptItem '{item.description}' created for receipt '{item.payment_receipt.receipt_number}' "
            f"by '{actor}' for company '{item.payment_receipt.company.name}'."
        )

    def perform_update(self, serializer):
        user = self.request.user
        company = get_logged_in_company(self.request)

        item = serializer.save()
        # Update receipt amount after item update
        item.payment_receipt.update_amount_received()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.info(
            f"PaymentReceiptItem '{item.description}' updated for receipt '{item.payment_receipt.receipt_number}' "
            f"by '{actor}' for company '{item.payment_receipt.company.name}'."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = get_logged_in_company(self.request)

        receipt_number = instance.payment_receipt.receipt_number
        description = instance.description
        # Update receipt amount before deletion
        instance.payment_receipt.update_amount_received()
        instance.delete()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.warning(
            f"PaymentReceiptItem '{description}' deleted for receipt '{receipt_number}' "
            f"by '{actor}' from company '{company.name}'."
        )
