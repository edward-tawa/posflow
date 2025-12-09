from rest_framework.viewsets import ModelViewSet
from inventory.models.product_category_model import ProductCategory
from inventory.serializers.product_category_serializer import ProductCategorySerializer
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from inventory.permissions.inventory_permissions import InventoryPermission
from rest_framework.filters import SearchFilter, OrderingFilter
from config.pagination.pagination import StandardResultsSetPagination
from config.utilities.get_queryset import get_company_queryset  # helper function
from company.models.company_model import Company
from loguru import logger


class ProductCategoryViewSet(ModelViewSet):
    """
    ViewSet for viewing and managing product categories.
    Includes detailed logging for all operations.
    """
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    authentication_classes = [CompanyCookieJWTAuthentication, UserCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [InventoryPermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # reusable helper function
        return get_company_queryset(self.request, ProductCategory)

    def perform_create(self, serializer):
        user = self.request.user
        company_or_user = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        category = serializer.save(company=company_or_user)
        identifier = getattr(company_or_user, 'name', None) or getattr(company_or_user, 'username', None) or 'Unknown'
        logger.success(f"Category '{category.name}' created by {identifier} in company '{getattr(company_or_user, 'name', 'Unknown')}'.")

    def perform_update(self, serializer):
        user = self.request.user
        company_or_user = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        category = serializer.save()
        identifier = getattr(company_or_user, 'name', None) or getattr(company_or_user, 'username', None) or 'Unknown'
        logger.info(f"Category '{category.name}' updated by {identifier}.")

    def perform_destroy(self, instance):
        user = self.request.user
        company_or_user = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        identifier = getattr(company_or_user, 'name', None) or getattr(company_or_user, 'username', None) or 'Unknown'
        logger.warning(f"Category '{instance.name}' deleted by {identifier}.")
        instance.delete()
