from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from sales.permissions.sales_permissions import SalesPermissions
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.utilities.pagination import StandardResultsSetPagination
from sales.models.sales_invoice_item_model import SalesInvoiceItem
from sales.serializers.sales_invoice_item_serializer import SalesInvoiceItemSerializer
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
    permission_classes = [SalesPermissions]

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
