from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.utilities.pagination import StandardResultsSetPagination
from taxes.models.fiscal_invoice_item_model import FiscalInvoiceItem
from taxes.serializers.fiscal_invoice_item_serializer import FiscalInvoiceItemSerializer
from taxes.permissions.fiscalisation_permissions import FiscalisationPermissions
from loguru import logger


class FiscalInvoiceItemViewSet(ModelViewSet):
    """
    ViewSet for managing Fiscal Invoice Items.
    Supports listing, retrieving, creating, updating, and deleting invoice items.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = FiscalInvoiceItem.objects.all()
    serializer_class = FiscalInvoiceItemSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [FiscalisationPermissions]

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'description',
        'fiscal_invoice__fiscal_code',
        'sale_item__description'
    ]
    ordering_fields = ['created_at', 'updated_at', 'description']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        Returns the FiscalInvoiceItem queryset filtered by the logged-in company/user.
        """
        return (
            get_company_queryset(self.request, FiscalInvoiceItem)
            .select_related(
                'fiscal_invoice',
                'fiscal_invoice__company',
                'sale_item'
            )
        )

    def perform_create(self, serializer):
        """
        Saves a new FiscalInvoiceItem instance and logs the event.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"FiscalInvoiceItem '{item.description}' created by '{actor}' "
            f"for FiscalInvoice '{item.fiscal_invoice.id}'."
        )

    def perform_update(self, serializer):
        """
        Saves an updated FiscalInvoiceItem instance and logs the event.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"FiscalInvoiceItem '{item.description}' updated by '{actor}' "
            f"for FiscalInvoice '{item.fiscal_invoice.id}'."
        )

    def perform_destroy(self, instance):
        """
        Deletes a FiscalInvoiceItem instance and logs the event.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        desc = instance.description
        invoice_id = instance.fiscal_invoice.id
        instance.delete()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.warning(
            f"FiscalInvoiceItem '{desc}' deleted by '{actor}' "
            f"from FiscalInvoice '{invoice_id}'."
        )
