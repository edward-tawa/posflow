from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from sales.permissions.sales_permissions import SalesPermissions
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from sales.models.sale_model import Sale
from sales.serializers.sale_serializer import SaleSerializer
from loguru import logger


class SalesViewSet(ModelViewSet):
    """
    ViewSet for managing Sales.
    Supports listing, retrieving, creating, updating, and deleting sales.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [SalesPermissions]

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'sale_number',
        'customer__name',
        'branch__name',
        'company__name',
        'issued_by__username'
    ]
    ordering_fields = ['created_at', 'updated_at', 'sales_date', 'total_amount']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            GET_QUERYSET()
            -------------------
            Returns the Sales queryset filtered by the logged-in company/user.
            -------------------
            """
            return (
                get_company_queryset(self.request, Sale)
                .select_related('company', 'branch', 'customer', 'issued_by', 'sales_invoice', 'sales_receipt')
            )
        except Exception as e:
            logger.error(f"Error fetching Sales queryset: {e}")
            return Sale.objects.none()

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Saves a new Sales instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        sale = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"Sale '{sale.sale_number}' created by '{actor}' "
            f"for company '{sale.company.name}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Saves an updated Sales instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        sale = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"Sale '{sale.sale_number}' updated by '{actor}' "
            f"for company '{sale.company.name}'."
        )
