from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from sales.permissions.sales_product_permissions import SalesProductPermissions
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from sales.models.sales_invoice_item_model import SalesInvoiceItem
from sales.serializers.sales_invoice_item_serializer import SalesInvoiceItemSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from sales.services.sales_invoice_item_service import SalesInvoiceItemService
from sales.models.sales_invoice_model import SalesInvoice
from loguru import logger


class SalesInvoiceItemViewSet(ModelViewSet):
    """
    ViewSet for managing SalesInvoiceItems.
    Supports listing, retrieving, creating, updating, and deleting invoice items.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = SalesInvoiceItem.objects.all()
    serializer_class = SalesInvoiceItemSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [SalesProductPermissions]

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'product__name',
        'sales_invoice__invoice_number',
        'sales_invoice__customer__name',
        'sales_invoice__company__name'
    ]
    ordering_fields = ['created_at', 'updated_at', 'subtotal', 'total_price']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            GET_QUERYSET()
            -------------------
            Returns the SalesInvoiceItem queryset filtered by the logged-in company/user.
            -------------------
            """
            return (
                get_company_queryset(self.request, SalesInvoiceItem)
                .select_related('sales_invoice', 'sales_invoice__company', 'product')
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Saves a new SalesInvoiceItem instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"SalesInvoiceItem '{item.product_name}' created by '{actor}' "
            f"for company '{item.sales_invoice.company.name}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Saves an updated SalesInvoiceItem instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"SalesInvoiceItem '{item.product_name}' updated by '{actor}' "
            f"for company '{item.sales_invoice.company.name}'."
        )

    

    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create_items(self, request):
        try:
            invoice_id = request.data.get('invoice_id')
            items_data = request.data.get('items', [])
            invoice = SalesInvoice.objects.get(id=invoice_id)
            created_items = SalesInvoiceItemService.bulk_create_sales_invoice_items(items_data, invoice)
            serializer = self.get_serializer(created_items, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error bulk creating invoice items: {e}")
            return Response({"detail": "Error bulk creating items."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='mark-invoice-paid')
    def mark_invoice_as_paid(self, request):
        try:
            invoice_id = request.data.get('invoice_id')
            invoice = SalesInvoice.objects.get(id=invoice_id)
            updated_invoice = SalesInvoiceItemService.mark_invoice_as_paid(invoice)
            return Response({"invoice_number": updated_invoice.invoice_number, "status": updated_invoice.status}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error marking invoice as paid: {e}")
            return Response({"detail": "Error marking invoice as paid."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
