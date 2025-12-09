from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication

from config.auth.jwt_token_authentication import (
    CompanyCookieJWTAuthentication,
    UserCookieJWTAuthentication
)
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.utilities.pagination import StandardResultsSetPagination

from taxes.models.fiscalisation_response_model import FiscalisationResponse
from taxes.serializers.fiscal_response_serializer import FiscalisationResponseSerializer
from taxes.permissions.fiscalisation_permissions import FiscalisationPermissions

from loguru import logger


class FiscalisationResponseViewSet(ModelViewSet):
    """
    ViewSet for managing Fiscalisation Responses.
    Supports listing, retrieving, creating, updating, and deleting responses.
    Includes filtering, searching, ordering, and detailed logging.
    """

    queryset = FiscalisationResponse.objects.all()
    serializer_class = FiscalisationResponseSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [FiscalisationPermissions]

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'fiscal_invoice__invoice_number',
        'response_code',
        'response_message',
        'fiscal_code'
    ]
    ordering_fields = ['created_at', 'updated_at', 'fiscal_invoice__invoice_number']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            Returns FiscalisationResponse queryset filtered by logged-in company/user.
            """
            return (
                get_company_queryset(self.request, FiscalisationResponse)
                .select_related(
                    'fiscal_invoice',
                    'fiscal_invoice__company'
                )
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {e}"

    def perform_create(self, serializer):
        """
        Saves a new FiscalisationResponse instance and logs the event.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        response = serializer.save()
        invoice = response.fiscal_invoice

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"FiscalisationResponse '{response.id}' created by '{actor}' "
            f"for FiscalInvoice '{invoice.invoice_number}'."
        )

    def perform_update(self, serializer):
        """
        Saves an updated FiscalisationResponse instance and logs the event.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        response = serializer.save()
        invoice = response.fiscal_invoice

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"FiscalisationResponse '{response.id}' updated by '{actor}' "
            f"for FiscalInvoice '{invoice.invoice_number}'."
        )

    def perform_destroy(self, instance):
        """
        Deletes a FiscalisationResponse instance and logs the event.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        response_id = instance.id
        invoice_number = instance.fiscal_invoice.invoice_number

        instance.delete()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.warning(
            f"FiscalisationResponse '{response_id}' deleted by '{actor}' "
            f"for FiscalInvoice '{invoice_number}'."
        )
