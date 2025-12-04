from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from sales.permissions.sales_permissions import SalesPermissions
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.utilities.pagination import StandardResultsSetPagination
from sales.models.sales_quotation_item_model import SalesQuotationItem
from sales.serializers.sales_quotation_item_serializer import SalesQuotationItemSerializer
from loguru import logger


class SalesQuotationItemViewSet(ModelViewSet):
    """
    ViewSet for managing Sales Quotation Items.
    Supports listing, retrieving, creating, updating, and deleting quotation items.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = SalesQuotationItem.objects.all()
    serializer_class = SalesQuotationItemSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [SalesPermissions]

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['product__name', 'sales_quotation__quotation_number', 'company__name']
    ordering_fields = ['created_at', 'updated_at', 'quantity', 'unit_price', 'total_price']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        GET_QUERYSET()
        -------------------
        Returns the SalesQuotationItem queryset filtered by the logged-in company/user.
        -------------------
        """
        return (
            get_company_queryset(self.request, SalesQuotationItem)
            .select_related('sales_quotation', 'product', 'sales_quotation__company')
        )

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Saves a new SalesQuotationItem instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"SalesQuotationItem for product '{item.product.name}' created by '{actor}' "
            f"for company '{item.sales_quotation.company.name}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Saves an updated SalesQuotationItem instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"SalesQuotationItem for product '{item.product.name}' updated by '{actor}' "
            f"for company '{item.company.name}'."
        )
