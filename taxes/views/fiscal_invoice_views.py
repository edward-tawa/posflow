from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from taxes.models.fiscal_invoice_model import FiscalInvoice
from taxes.serializers.fiscal_invoice_serializer import FiscalInvoiceSerializer
from taxes.permissions.fiscalisation_permissions import FiscalisationPermissions
from loguru import logger


class FiscalInvoiceViewSet(ModelViewSet):
    """
    ViewSet for managing Fiscal Invoices.
    Supports listing, retrieving, creating, updating, and deleting invoices.
    Includes filtering, searching, ordering, and detailed logging.
    """

    queryset = FiscalInvoice.objects.all()
    serializer_class = FiscalInvoiceSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [FiscalisationPermissions]

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'invoice_number',
        'sale__invoice_number',
        'company__name',
        'branch__name',
        'device__device_serial_number'
    ]
    ordering_fields = ['created_at', 'updated_at', 'invoice_number', 'total_amount']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            Returns FiscalInvoice queryset filtered by logged-in company/user.
            """
            return (
                get_company_queryset(self.request, FiscalInvoice)
                .select_related(
                    'company',
                    'branch',
                    'device'
                    # 'sale'
                )
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {e}"

    def perform_create(self, serializer):
        """
        Saves a new FiscalInvoice instance and logs the event.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        invoice = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"FiscalInvoice '{invoice.invoice_number}' created by '{actor}' "
            f"for company '{invoice.company.name}'."
        )

    def perform_update(self, serializer):
        """
        Saves an updated FiscalInvoice instance and logs the event.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        invoice = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"FiscalInvoice '{invoice.invoice_number}' updated by '{actor}' "
            f"for company '{invoice.company.name}'."
        )

    def perform_destroy(self, instance):
        """
        Deletes a FiscalInvoice instance and logs the event.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        invoice_number = instance.invoice_number
        instance.delete()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.warning(
            f"FiscalInvoice '{invoice_number}' deleted by '{actor}' "
            f"from company '{company.name}'."
        )
