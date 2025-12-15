from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import (
    CompanyCookieJWTAuthentication,
    UserCookieJWTAuthentication
)
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from sales.models.sales_receipt_model import SalesReceipt
from sales.permissions.sales_permissions import SalesPermissions
from sales.serializers.sales_receipt_serializer import SalesReceiptSerializer
from sales.services.sales_receipt_service import SalesReceiptService
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.decorators import action
from loguru import logger


class SalesReceiptViewSet(ModelViewSet):
    """
    ViewSet for managing Sales Receipts.
    Supports listing, retrieving, creating, updating, and deleting receipts.
    Includes filtering, searching, ordering, and detailed logging.
    """

    queryset = SalesReceipt.objects.select_related(
        'company',
        'branch',
        'customer',
        'issued_by',
        'sales_payment'
    )
    serializer_class = SalesReceiptSerializer

    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [SalesPermissions]

    # Filtering & search
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'receipt_number',
        'customer__name',
        'branch__name',
        'company__name',
        'sales_payment__payment_number'
    ]
    ordering_fields = [
        'created_at',
        'updated_at',
        'receipt_date',
        'total_amount'
    ]
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            GET_QUERYSET()
            -------------------
            Returns SalesReceipt queryset filtered by logged-in company.
            -------------------
            """
            return (
                get_company_queryset(self.request, SalesReceipt)
                .select_related(
                    'company',
                    'branch',
                    'customer',
                    'issued_by',
                    'sales_payment'
                )
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Saves a new SalesReceipt instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        receipt = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"SalesReceipt '{receipt.receipt_number}' created by '{actor}' "
            f"for company '{receipt.company.name}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Saves an updated SalesReceipt instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        receipt = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"SalesReceipt '{receipt.receipt_number}' updated by '{actor}' "
            f"for company '{receipt.company.name}'."
        )


    @action(detail=True, methods=['post'], url_path='void')
    def void_receipt(self, request, pk=None):
        """
        Endpoint to void a SalesReceipt.
        """
        try:
            receipt = self.get_object()
            reason = request.data.get('reason', '')

            receipt = SalesReceiptService.void_receipt(receipt, reason)

            user = self.request.user
            company = get_logged_in_company(self.request)
            actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

            logger.warning(
                f"SalesReceipt '{receipt.receipt_number}' voided by '{actor}'. Reason: {reason}"
            )

            serializer = self.get_serializer(receipt)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error voiding SalesReceipt {pk}: {e}")
            return Response({"detail": "Error voiding receipt."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)