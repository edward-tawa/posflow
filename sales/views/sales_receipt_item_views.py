from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from sales.permissions.sales_permissions import SalesPermissions
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.utilities.pagination import StandardResultsSetPagination
from sales.models.sales_receipt_item_model import SalesReceiptItem
from sales.serializers.sales_receipt_item_serializer import SalesReceiptItemSerializer
from loguru import logger


class SalesReceiptItemViewSet(ModelViewSet):
    """
    ViewSet for managing Sales Receipt Items.
    Supports listing, retrieving, creating, updating, and deleting receipt items.
    Includes filtering, searching, ordering, and detailed logging.
    """

    queryset = SalesReceiptItem.objects.all()
    serializer_class = SalesReceiptItemSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [SalesPermissions]

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['product__name', 'sales_receipt__receipt_number']
    ordering_fields = ['created_at', 'updated_at', 'quantity', 'unit_price', 'total']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            GET_QUERYSET()
            -------------------
            Returns the SalesReceiptItem queryset filtered by the logged-in company/user.
            -------------------
            """
            return (
                get_company_queryset(self.request, SalesReceiptItem)
                .select_related('sales_receipt', 'product', 'sales_receipt__company')
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {e}"

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Saves a new SalesReceiptItem instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"SalesReceiptItem for product '{item.product.name}' created by '{actor}' "
            f"for company '{item.sales_receipt.company.name}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Saves an updated SalesReceiptItem instance and logs the event.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"SalesReceiptItem for product '{item.product.name}' updated by '{actor}' "
            f"for company '{item.sales_receipt.company.name}'."
        )
