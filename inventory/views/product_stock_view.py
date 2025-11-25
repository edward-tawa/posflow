from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.utilities.pagination import StandardResultsSetPagination
from inventory.models.product_stock_model import ProductStock
from inventory.serializers.product_stock_serializer import ProductStockSerializer
from inventory.permissions.inventory_permissions import InventoryPermission
from inventory.django_filters.product_stock_filter import ProductStockFilter
from company.models.company_model import Company
from loguru import logger


class ProductStockViewSet(ModelViewSet):
    """
    ViewSet for managing ProductStock entries.
    Supports listing, retrieving, creating, updating, and deleting stocks.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = ProductStock.objects.all()
    serializer_class = ProductStockSerializer
    authentication_classes = [CompanyCookieJWTAuthentication, UserCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [InventoryPermission]

    # Filtering & search
    filter_backends = [SearchFilter, OrderingFilter]
    filterset_class = ProductStockFilter
    search_fields = ['product__name', 'branch__name']
    ordering_fields = ['quantity', 'updated_at', 'created_at']
    ordering = ['-updated_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Return ProductStock queryset filtered by the logged-in company/user."""
        return get_company_queryset(self.request, ProductStock)

    def perform_create(self, serializer):
        user = self.request.user
        company = get_logged_in_company(self.request)
        product_stock = serializer.save()

        # Determine identifier for logging
        identifier = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        branch_name = getattr(product_stock.branch, 'name', 'Unknown')

        logger.success(
            f"ProductStock for product '{product_stock.product.name}' in branch '{branch_name}' created by '{identifier}'."
        )

    def perform_update(self, serializer):
        user = self.request.user
        company = get_logged_in_company(self.request)
        product_stock = serializer.save()

        identifier = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        branch_name = getattr(product_stock.branch, 'name', 'Unknown')

        logger.info(
            f"ProductStock for product '{product_stock.product.name}' in branch '{branch_name}' updated by '{identifier}'."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = get_logged_in_company(self.request)

        identifier = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        branch_name = getattr(instance.branch, 'name', 'Unknown')

        logger.warning(
            f"ProductStock for product '{instance.product.name}' in branch '{branch_name}' deleted by '{identifier}'."
        )
        instance.delete()
