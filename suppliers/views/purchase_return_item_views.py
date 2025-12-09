from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.utilities.get_company_or_user_company import get_expected_company
from config.utilities.pagination import StandardResultsSetPagination
from suppliers.models.purchase_return_item_model import PurchaseReturnItem
from suppliers.serializers.purchase_return_item_serializer import PurchaseReturnItemSerializer
from suppliers.permissions.supplier_permissions import SupplierPermissions
from loguru import logger


class PurchaseReturnItemViewSet(ModelViewSet):
    """
    ViewSet for managing Purchase Return Items.
    Supports listing, retrieving, creating, updating, and deleting purchase return items.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = PurchaseReturnItem.objects.all()
    serializer_class = PurchaseReturnItemSerializer
    authentication_classes = [CompanyCookieJWTAuthentication, UserCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [SupplierPermissions]

    # Filtering & search
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['purchase_return__purchase_return_number', 'product__name']
    ordering_fields = ['created_at', 'updated_at', 'quantity', 'unit_price']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            GET_QUERYSET()
            -------------------
            Returns the PurchaseReturnItem queryset filtered by the logged-in company/user.
            -------------------
            """
            return get_company_queryset(self.request, PurchaseReturnItem).select_related('purchase_return', 'product')
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {e}"

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Creates a new PurchaseReturnItem instance and logs the action.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)
        purchase_return_item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', None)

        logger.success(
            f"PurchaseReturnItem for product '{purchase_return_item.product.name}' created by '{actor}' "
            f"under PurchaseReturn '{purchase_return_item.purchase_return.purchase_return_number}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Updates an existing PurchaseReturnItem instance and logs the action.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)
        purchase_return_item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"PurchaseReturnItem for product '{purchase_return_item.product.name}' updated by '{actor}' "
            f"under PurchaseReturn '{purchase_return_item.purchase_return.purchase_return_number}'."
        )
