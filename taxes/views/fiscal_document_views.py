from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from taxes.models.fiscal_document_model import FiscalDocument
from taxes.serializers.fiscal_document_serializer import FiscalDocumentSerializer
from taxes.permissions.fiscalisation_permissions import FiscalisationPermissions
from loguru import logger


class FiscalDocumentViewSet(ModelViewSet):
    """
    ViewSet for managing Fiscal Documents.
    Supports listing, retrieving, creating, updating, and deleting fiscal documents.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = FiscalDocument.objects.all()
    serializer_class = FiscalDocumentSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [FiscalisationPermissions]

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'fiscal_code',
        'qr_code',
        'company__name',
        'branch__name'
    ]
    ordering_fields = ['created_at', 'updated_at', 'fiscal_code']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            Returns the FiscalDocument queryset filtered by the logged-in company/user.
            """
            return (
                get_company_queryset(self.request, FiscalDocument)
                .select_related('company', 'branch', 'device')
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        """
        Saves a new FiscalDocument instance and logs the event.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        fiscal_doc = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"FiscalDocument '{fiscal_doc.id}' created by '{actor}' "
            f"for company '{fiscal_doc.company.name}'."
        )

    def perform_update(self, serializer):
        """
        Saves an updated FiscalDocument instance and logs the event.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        fiscal_doc = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"FiscalDocument '{fiscal_doc.id}' updated by '{actor}' "
            f"for company '{fiscal_doc.company.name}'."
        )

    def perform_destroy(self, instance):
        """
        Deletes a FiscalDocument instance and logs the event.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        doc_id = instance.id
        instance.delete()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.warning(
            f"FiscalDocument '{doc_id}' deleted by '{actor}' "
            f"from company '{company.name}'."
        )
