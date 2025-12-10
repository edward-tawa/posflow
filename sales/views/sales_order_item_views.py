from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from sales.permissions.sales_permissions import SalesPermissions
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from sales.models.sales_order_item_model import SalesOrderItem
from sales.serializers.sales_order_item_serializer import SalesOrderItemSerializer
from loguru import logger


class SalesOrderItemViewSet(ModelViewSet):
    """
    ViewSet for managing Sales Order Items.
    Supports listing, retrieving, creating, updating, and deleting sales order items.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = SalesOrderItem.objects.all()
    serializer_class = SalesOrderItemSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [SalesPermissions]

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'product__name',
        'sales_order__order_number',
        'sales_order__customer_name',
        'sales_order__company__name'
    ]
    ordering_fields = ['created_at', 'updated_at', 'quantity', 'total_price']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            GET_QUERYSET()
            -------------------
            Returns the SalesOrderItem queryset filtered by the logged-in company/user.
            -------------------
            """
            return (
                get_company_queryset(self.request, SalesOrderItem)
                .select_related('product', 'sales_order', 'sales_order__company')
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Saves a new SalesOrderItem instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"SalesOrderItem '{item.product_name}' created by '{actor}' "
            f"for SalesOrder '{item.sales_order.order_number}' and company '{item.sales_order.company.name}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Saves an updated SalesOrderItem instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"SalesOrderItem '{item.product_name}' updated by '{actor}' "
            f"for SalesOrder '{item.sales_order.order_number}' and company '{item.sales_order.company.name}'."
        )
