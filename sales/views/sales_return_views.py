from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from sales.permissions.sales_permissions import SalesPermissions
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.utilities.pagination import StandardResultsSetPagination
from sales.models.sales_return_model import SalesReturn
from sales.serializers.sales_return_serializer import SalesReturnSerializer
from loguru import logger


class SalesReturnViewSet(ModelViewSet):
    """
    ViewSet for managing Sales Returns.
    Supports listing, retrieving, creating, updating, and deleting sales returns.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = SalesReturn.objects.all()
    serializer_class = SalesReturnSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]

    # If you want permissions later, plug them in here.
    permission_classes = [SalesPermissions]

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['return_number', 'sale_order__order_number', 'customer__name', 'company__name']
    ordering_fields = ['created_at', 'updated_at', 'return_date', 'total_amount']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        GET_QUERYSET()
        -------------------
        Returns the SalesReturn queryset filtered by the logged-in company/user.
        -------------------
        """
        return (
            get_company_queryset(self.request, SalesReturn)
            .select_related('company', 'branch', 'customer', 'sale_order')
        )

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Saves a new SalesReturn instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        sales_return = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"SalesReturn '{sales_return.return_number}' created by '{actor}' "
            f"for company '{sales_return.company.name}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Saves an updated SalesReturn instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        sales_return = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"SalesReturn '{sales_return.return_number}' updated by '{actor}' "
            f"for company '{sales_return.company.name}'."
        )