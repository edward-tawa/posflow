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
# from sales.models.sales_return_item_model import SalesReturnItem 'SALES RETURN ITEM CLASS DOES NOT EXIST IN sales_return_item_model.py'
from sales.permissions.sales_permissions import SalesPermissions
from sales.serializers.sales_return_item_serializer import SalesReturnItemSerializer
from loguru import logger


class SalesReturnItemViewSet(ModelViewSet):
    """
    ViewSet for managing Sales Return Items.
    Supports listing, retrieving, creating, updating, and deleting items.
    Includes filtering, searching, ordering, and structured logging.
    """

    # queryset = SalesReturnItem.objects.select_related(
    #     'sales_return',
    #     'product'
    # )
    serializer_class = SalesReturnItemSerializer

    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [SalesPermissions]

    # Filtering & search
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'product_name',
        'product__name',
        'sales_return__return_number',
        'sales_return__customer__name'
    ]
    ordering_fields = [
        'created_at',
        'updated_at',
        'quantity',
        'unit_price',
        'total_price'
    ]
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        GET_QUERYSET()
        -------------------
        Returns items filtered by the logged-in company
        using the parent sales_return.company relationship.
        -------------------
        """
        return (
            get_company_queryset(
                self.request,
                SalesReturnItem,
                parent_field='sales_return__company'
            )
            .select_related('sales_return', 'product')
        )

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Creates a SalesReturnItem and logs the action.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"SalesReturnItem '{item.product_name}' added to SalesReturn '{item.sales_return.return_number}' "
            f"by '{actor}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Updates a SalesReturnItem and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"SalesReturnItem '{item.product_name}' updated on SalesReturn '{item.sales_return.return_number}' "
            f"by '{actor}'."
        )
