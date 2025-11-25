from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from sales.permissions.sales_permissions import SalesPermissions
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.utilities.pagination import StandardResultsSetPagination
from sales.models.sales_quotation_model import SalesQuotation
from sales.serializers.sales_quotation_serializer import SalesQuotationSerializer
from loguru import logger


class SalesQuotationViewSet(ModelViewSet):
    """
    ViewSet for managing Sales Quotations.
    Supports listing, retrieving, creating, updating, and deleting quotations.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = SalesQuotation.objects.all()
    serializer_class = SalesQuotationSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [SalesPermissions]

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['quotation_number', 'customer__name', 'company__name']
    ordering_fields = ['created_at', 'updated_at', 'quotation_date', 'total_amount']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        GET_QUERYSET()
        -------------------
        Returns the SalesQuotation queryset filtered by the logged-in company/user.
        -------------------
        """
        return (
            get_company_queryset(self.request, SalesQuotation)
            .select_related('company', 'branch', 'customer', 'created_by')
        )

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Saves a new SalesQuotation instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        quotation = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"SalesQuotation '{quotation.quotation_number}' created by '{actor}' "
            f"for company '{quotation.company.name}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Saves an updated SalesQuotation instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        quotation = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"SalesQuotation '{quotation.quotation_number}' updated by '{actor}' "
            f"for company '{quotation.company.name}'."
        )
