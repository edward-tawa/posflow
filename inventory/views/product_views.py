from rest_framework.viewsets import ModelViewSet
from inventory.models.product_model import Product
from inventory.serializers.product_serializer import ProductSerializer
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from inventory.permissions.inventory_permissions import InventoryPermission
from rest_framework.filters import SearchFilter, OrderingFilter
from config.utilities.pagination import StandardResultsSetPagination
from company.models.company_model import Company
from loguru import logger


class ProductViewSet(ModelViewSet):
    """
    ViewSet for viewing and managing products.
    Supports listing, retrieving, creating, updating, and deleting products.
    Includes detailed logging for key operations.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [CompanyCookieJWTAuthentication, UserCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [InventoryPermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description', 'category__name', 'company__name', 'price']
    ordering_fields = ['name', 'price', 'stock_quantity', 'created_at', 'company__name', 'category__name']
    ordering = ['name']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            logger.warning("Unauthenticated access attempt to ProductViewSet.")
            return Product.objects.none()

        # Determine the "company context"
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        identifier = getattr(company, 'name', None) or getattr(company, 'username', None) or 'Unknown'

        if not company:
            logger.warning(f"{identifier} has no associated company.")
            return Product.objects.none()

        logger.info(f"{identifier} fetching products for company '{getattr(company, 'name', 'Unknown')}'.")
        return Product.objects.filter(company=company).select_related('category', 'company')

    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        product = serializer.save(company=company)
        identifier = getattr(company, 'name', None) or getattr(company, 'username', None) or 'Unknown'
        logger.success(f"Product '{product.name}' created by {identifier} in company '{getattr(company, 'name', 'Unknown')}'.")

    def perform_update(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        product = serializer.save()
        identifier = getattr(company, 'name', None) or getattr(company, 'username', None) or 'Unknown'
        logger.info(f"Product '{product.name}' updated by {identifier}.")

    def perform_destroy(self, instance):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        identifier = getattr(company, 'name', None) or getattr(company, 'username', None) or 'Unknown'
        logger.warning(f"Product '{instance.name}' deleted by {identifier}.")
        instance.delete()
