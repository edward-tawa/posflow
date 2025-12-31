from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from company.models.company_model import Company
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_company_or_user_company import get_expected_company
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from config.utilities.get_queryset import get_company_queryset
from suppliers.services.purchase_invoice_service import PurchaseInvoiceService
from suppliers.models.purchase_invoice_model import PurchaseInvoice
from suppliers.serializers.purchase_invoice_serializer import PurchaseInvoiceSerializer
from suppliers.permissions.supplier_permissions import SupplierPermissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from loguru import logger


class PurchaseInvoiceViewSet(ModelViewSet):
    """
    ViewSet for managing Purchase Invoices.
    Supports listing, retrieving, creating, updating, and deleting invoices.
    Includes filtering, searching, ordering, company validation, and detailed logging.
    """

    queryset = PurchaseInvoice.objects.all()
    serializer_class = PurchaseInvoiceSerializer

    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [SupplierPermissions]

    # Filtering & search
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['invoice_number', 'supplier__name', 'purchase_order__order_number']
    ordering_fields = ['invoice_date', 'total_amount', 'created_at', 'updated_at']
    ordering = ['-invoice_date']

    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """Return invoices belonging to the logged-in user's company."""
            return (
                get_company_queryset(self.request, PurchaseInvoice)
                .select_related('supplier', 'purchase_order', 'company', 'branch', 'issued_by')
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        """Create PurchaseInvoice with company and logging enforcement."""
        request = self.request
        user = request.user
        company = get_logged_in_company(request)

        # Save invoice with company auto-bound
        invoice = serializer.save(company=company)

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.info(company)
        #Request should contain user id
        logger.success(
            f"PurchaseInvoice '{invoice.invoice_number}' created for supplier '{invoice.supplier}' "
            f"in company '{company.name if company else None}' by {actor}."
        )

    def perform_update(self, serializer):
        """Update PurchaseInvoice with company validation and logging."""
        request = self.request
        user = request.user
        company = get_logged_in_company(request)

        invoice = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"PurchaseInvoice '{invoice.invoice_number}' updated by '{actor}'."
        )


    @action(detail=True, methods=['post'], url_path='detach-from-supplier')
    def detach_from_supplier(self, request, pk=None):
        invoice = self.get_object()
        invoice = PurchaseInvoiceService.detach_from_supplier(invoice)
        return Response(self.get_serializer(invoice).data, status=status.HTTP_200_OK)

    # -------------------------
    # UPDATE STATUS
    # -------------------------
    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        invoice = self.get_object()
        new_status = request.data.get('status')
        if not new_status:
            return Response({"error": "status is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            invoice = PurchaseInvoiceService.update_invoice_status(invoice, new_status)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(invoice).data, status=status.HTTP_200_OK)

    # -------------------------
    # APPROVE INVOICE
    # -------------------------
    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        invoice = self.get_object()
        try:
            invoice = PurchaseInvoiceService.approve_invoice(invoice)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(invoice).data, status=status.HTTP_200_OK)