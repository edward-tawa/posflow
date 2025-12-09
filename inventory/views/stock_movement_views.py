from rest_framework.viewsets import ModelViewSet
from inventory.models.stock_movement_model import StockMovement
from inventory.serializers.stock_movement_serializer import StockMovementSerializer
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from inventory.permissions.inventory_permissions import InventoryPermission
from rest_framework.filters import SearchFilter, OrderingFilter
from config.utilities.pagination import StandardResultsSetPagination
from config.utilities.get_queryset import get_company_queryset
from company.models.company_model import Company
from loguru import logger


class StockMovementViewSet(ModelViewSet):
    """
    ViewSet for managing Stock Movements.
    Includes company-level access control, logging, search, ordering, and pagination.
    """
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    authentication_classes = [CompanyCookieJWTAuthentication, UserCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [InventoryPermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['reference_number', 'movement_type']
    ordering_fields = ['movement_date', 'created_at', 'quantity']
    ordering = ['-movement_date']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            # Return only stock movements for the user's company
            return get_company_queryset(self.request, StockMovement).select_related(
                'company', 'branch', 'product', 'sales_order', 'sales_return', 'purchase_order', 'purchase_return'
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {e}"

    def perform_create(self, serializer):
        user = self.request.user
        company_or_user = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        stock_movement = serializer.save(company=company_or_user)
        identifier = getattr(company_or_user, 'name', None) or getattr(company_or_user, 'username', None) or 'Unknown'
        logger.success(f"StockMovement '{stock_movement.reference_number}' created by {identifier} in company '{getattr(company_or_user, 'name', 'Unknown')}'.")

    def perform_update(self, serializer):
        user = self.request.user
        company_or_user = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        instance = serializer.save()
        identifier = getattr(company_or_user, 'name', None) or getattr(company_or_user, 'username', None) or 'Unknown'
        logger.info(f"StockMovement '{instance.reference_number}' updated by {identifier}.")

    def perform_destroy(self, instance):
        user = self.request.user
        company_or_user = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        identifier = getattr(company_or_user, 'name', None) or getattr(company_or_user, 'username', None) or 'Unknown'
        logger.warning(f"StockMovement '{instance.reference_number}' deleted by {identifier}.")
        instance.delete()