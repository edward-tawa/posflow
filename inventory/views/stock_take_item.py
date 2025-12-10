from rest_framework.viewsets import ModelViewSet
from inventory.models.stock_take_item_model import StockTakeItem
from inventory.serializers.stock_take_item_serializer import StockTakeItemSerializer
from inventory.permissions.inventory_permissions import InventoryPermission
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from company.models.company_model import Company
from rest_framework.filters import SearchFilter, OrderingFilter
from config.pagination.pagination import StandardResultsSetPagination
from loguru import logger



class StockTakeItemViewSet(ModelViewSet):
    """
    ViewSet for viewing and managing stock take items.
    Supports listing, retrieving, creating, updating, and deleting stock take items.
    Includes detailed logging for key operations.
    """
    queryset = StockTakeItem.objects.all()
    serializer_class = StockTakeItemSerializer
    authentication_classes = [CompanyCookieJWTAuthentication, UserCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [InventoryPermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['stock_take__reference_number', 'product__name', 'status']
    ordering_fields = ['created_at', 'updated_at', 'status']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            user = self.request.user
            if not user.is_authenticated:
                logger.warning("Unauthenticated access attempt to StockTakeItemViewSet.")
                return StockTakeItem.objects.none()

            # Determine the "company context" for this request
            company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)

            # Determine an identifier for logging: either name (company) or username (user)
            identifier = getattr(company, 'name', None) or getattr(company, 'username', None) or 'Unknown'

            if not company:
                logger.warning(f"{identifier} has no associated company context.")
                return StockTakeItem.objects.none()

            logger.info(f"{identifier} fetching stock take items for company '{getattr(company, 'name', 'Unknown')}'.")
            return StockTakeItem.objects.filter(stock_take__company=company).select_related('stock_take', 'product')
        except Exception as e:
            logger.error(e)
            return self.queryset.none()
