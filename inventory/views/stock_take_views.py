from rest_framework.viewsets import ModelViewSet
from inventory.models.stock_take_model import StockTake
from inventory.serializers.stock_take_serializer import StockTakeSerializer
from inventory.permissions.inventory_permissions import InventoryPermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from config.pagination.pagination import StandardResultsSetPagination
from loguru import logger


class StockTakeViewSet(ModelViewSet):
    """
    Handles creating, listing, updating, and deleting stocktakes.
    Logs all critical user actions for traceability.
    """
    queryset = StockTake.objects.all()
    serializer_class = StockTakeSerializer
    permission_classes = [InventoryPermission]
    authentication_classes = [CompanyCookieJWTAuthentication, UserCookieJWTAuthentication, JWTAuthentication]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['reference_number', 'performed_by__username', 'performed_by__first_name', 'performed_by__last_name', 'status']
    ordering_fields = ['counted_at', 'created_at', 'updated_at', 'status']
    ordering = ['-counted_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            logger.warning("Unauthorized access attempt to StockTakeViewSet.")
            return StockTake.objects.none()

        company = getattr(user, 'company', None)
        if company:
            logger.info(f"User '{user.username}' retrieved stocktakes for company '{company.name}'.")
            return StockTake.objects.filter(company=company)
        logger.warning(f"User '{user.username}' has no associated company. Returning empty queryset.")
        return StockTake.objects.none()

    def perform_create(self, serializer):
        logger.info(self.request.user.branch)
        stock_take = serializer.save(
            company = self.request.user.company, 
            branch = self.request.user.branch, 
            performed_by = self.request.user
        )
        user = self.request.user
        logger.success(
            f"StockTake created by '{user.username}' ({user.role}) "
            f"for company '{stock_take.company.name}' "
            f"at branch '{stock_take.branch.name}' "
            f"with reference '{stock_take.reference_number}'."
        )

    def perform_update(self, serializer):
        stock_take = serializer.save()
        user = self.request.user
        logger.info(
            f"StockTake '{stock_take.reference_number}' updated by '{user.username}' ({user.role}). "
            f"Status: {stock_take.status}."
        )

    def perform_destroy(self, instance):
        ref = instance.reference_number
        company_name = instance.company.name
        user = self.request.user
        instance.delete()
        logger.warning(
            f"StockTake '{ref}' deleted by '{user.username}' from company '{company_name}'."
        )
