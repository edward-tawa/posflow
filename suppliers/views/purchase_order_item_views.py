from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.utilities.pagination import StandardResultsSetPagination
from suppliers.models.purchase_order_item_model import PurchaseOrderItem
from suppliers.serializers.purchase_order_item_serializer import PurchaseOrderItemSerializer
from suppliers.permissions.supplier_permissions import SupplierPermissions
from loguru import logger



class PurchaseOrderItemViewSet(ModelViewSet):
    """
    ViewSet for managing Purchase Order Items.
    Supports listing, retrieving, creating, updating, and deleting purchase order items.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = PurchaseOrderItem.objects.all()
    serializer_class = PurchaseOrderItemSerializer
    authentication_classes = [CompanyCookieJWTAuthentication, UserCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [SupplierPermissions]

    # Filtering & search
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['purchase_order__order_number', 'product__name', 'status']
    ordering_fields = ['created_at', 'updated_at', 'status']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        GET_QUERYSET()
        -------------------
        Returns the PurchaseOrderItem queryset filtered by the logged-in company/user.
        -------------------
        """
        """Return PurchaseOrderItem queryset filtered by the logged-in company/user."""
        return get_company_queryset(self.request, PurchaseOrderItem).select_related('purchase_order', 'product')

    def perform_create(self, serializer):
        """
        PERFORM_CREATE()
        -------------------
        Creates a new PurchaseOrderItem instance and logs the action.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)
        purchase_order_item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"PurchaseOrderItem for product '{purchase_order_item.product.name}' created by '{actor}'."
        )

    def perform_update(self, serializer):
        """
        PERFORM_UPDATE()
        -------------------
        Updates an existing PurchaseOrderItem instance and logs the action.
        -------------------
        """
        user = self.request.user
        company = get_logged_in_company(self.request)
        purchase_order_item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"PurchaseOrderItem for product '{purchase_order_item.product.name}' updated by '{actor}'."
        )