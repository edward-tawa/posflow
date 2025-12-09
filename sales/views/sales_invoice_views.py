from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from sales.permissions.sales_permissions import SalesPermissions
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.utilities.pagination import StandardResultsSetPagination
from sales.models.sales_invoice_model import SalesInvoice
from sales.serializers.sales_invoice_serializer import SalesInvoiceSerializer
from loguru import logger


class SalesInvoiceViewSet(ModelViewSet):
    """
    ViewSet for managing Sales Invoices.
    Supports listing, retrieving, creating, updating, and deleting sales invoices.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = SalesInvoice.objects.all()
    serializer_class = SalesInvoiceSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [SalesPermissions]

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'invoice_number',
        'customer__name',
        'company__name',
        'branch__name'
    ]
    ordering_fields = ['created_at', 'updated_at', 'invoice_date', 'total_amount']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            GET_QUERYSET()
            -------------------
            Returns the SalesInvoice queryset filtered by the logged-in company/user.
            -------------------
            """
            return (
                get_company_queryset(self.request, SalesInvoice)
                .select_related('company', 'branch', 'customer', 'issued_by')
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {e}"

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Saves a new SalesInvoice instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        invoice = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"SalesInvoice '{invoice.invoice_number}' created by '{actor}' "
            f"for company '{invoice.company.name}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Saves an updated SalesInvoice instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        invoice = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"SalesInvoice '{invoice.invoice_number}' updated by '{actor}' "
            f"for company '{invoice.company.name}'."
        )
