from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from payments.models import PaymentReceipt
from payments.serializers.payment_receipt_serializer import PaymentReceiptSerializer
from payments.permissions.payment_permissions import PaymentsPermissions
from payments.services.payment_receipt_service import PaymentReceiptService
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from loguru import logger


class PaymentReceiptViewSet(ModelViewSet):
    """
    ViewSet for managing PaymentReceipts.
    Supports listing, retrieving, creating, updating, and deleting receipts.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = PaymentReceipt.objects.all()
    serializer_class = PaymentReceiptSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [PaymentsPermissions]

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'receipt_number',
        'company__name',
        'branch__name',
        'payment__payment_number',
        'issued_by__name'
    ]
    ordering_fields = ['created_at', 'updated_at', 'receipt_date', 'amount']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            Returns PaymentReceipt queryset filtered by the logged-in company/user.
            """
            return (
                get_company_queryset(self.request, PaymentReceipt)
                .select_related('company', 'branch', 'payment', 'issued_by')
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        company = get_logged_in_company(self.request)

        receipt = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"PaymentReceipt '{receipt.receipt_number}' created by '{actor}' "
            f"for company '{receipt.company.name}'."
        )

    def perform_update(self, serializer):
        user = self.request.user
        company = get_logged_in_company(self.request)

        receipt = serializer.save()
        # Recalculate total amount after update
        receipt.update_amount_received()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.info(
            f"PaymentReceipt '{receipt.receipt_number}' updated by '{actor}' "
            f"for company '{receipt.company.name}'."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = get_logged_in_company(self.request)

        receipt_number = instance.receipt_number
        instance.delete()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.warning(
            f"PaymentReceipt '{receipt_number}' deleted by '{actor}' "
            f"from company '{company.name}'."
        )


    @action(detail=True, methods=['post'], url_path='send')
    def send_receipt(self, request, pk=None):
        receipt = self.get_object()
        PaymentReceiptService.mark_receipt_as_sent(receipt)
        return Response({"status": "SENT"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_receipt(self, request, pk=None):
        receipt = self.get_object()
        PaymentReceiptService.mark_receipt_as_cancelled(receipt)
        return Response({"status": "CANCELLED"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        receipt = self.get_object()
        new_status = request.data.get("status")
        PaymentReceiptService.update_payment_receipt_status(receipt, new_status)
        return Response({"status": new_status}, status=status.HTTP_200_OK)

    # -------------------------
    # RELATION ACTIONS
    # -------------------------
    @action(detail=True, methods=['post'], url_path='attach-relation')
    def attach_relation(self, request, pk=None):
        receipt = self.get_object()
        relation_field = request.data.get("relation_field")
        entity_id = request.data.get("entity_id")
        PaymentReceiptService.attach_relation(receipt, relation_field, entity_id)
        return Response({f"{relation_field}_id": entity_id}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='detach-relation')
    def detach_relation(self, request, pk=None):
        receipt = self.get_object()
        relation_field = request.data.get("relation_field")
        PaymentReceiptService.detach_relation(receipt, relation_field)
        return Response({f"{relation_field}_detached": True}, status=status.HTTP_200_OK)