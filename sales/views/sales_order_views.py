from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from sales.permissions.sales_permissions import SalesPermissions
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.utilities.pagination import StandardResultsSetPagination
from sales.models.sales_order_model import SalesOrder
from sales.serializers.sales_order_serializer import SalesOrderSerializer
from loguru import logger


class SalesOrderViewSet(ModelViewSet):
    """
    ViewSet for managing Sales Orders.
    Supports listing, retrieving, creating, updating, and deleting sales orders.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [SalesPermissions]

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'order_number',
        'customer__name',
        'branch__name',
        'company__name',
        'cashier__username'
    ]
    ordering_fields = ['created_at', 'updated_at', 'order_date', 'total_amount']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        GET_QUERYSET()
        -------------------
        Returns the SalesOrder queryset filtered by the logged-in company/user.
        -------------------
        """
        return (
            get_company_queryset(self.request, SalesOrder)
            .select_related('company', 'branch', 'customer', 'cashier')
        )

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Saves a new SalesOrder instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        order = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"SalesOrder '{order.order_number}' created by '{actor}' "
            f"for company '{order.company.name}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Saves an updated SalesOrder instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        order = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"SalesOrder '{order.order_number}' updated by '{actor}' "
            f"for company '{order.company.name}'."
        )
