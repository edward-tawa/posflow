from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework import status
from inventory.models.stock_adjustment_model import StockAdjustment
from inventory.serializers.stock_adjustment_serializer import StockAdjustmentSerializer
from inventory.permissions.inventory_permissions import InventoryPermission
from config.auth.jwt_token_authentication import (
    CompanyCookieJWTAuthentication,
    UserCookieJWTAuthentication,
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.pagination.pagination import StandardResultsSetPagination
from company.models.company_model import Company
from loguru import logger


class StockAdjustmentViewSet(ModelViewSet):
    """
    ViewSet for viewing and creating stock adjustments.
    Stock adjustments are immutable once created.
    """
    queryset = StockAdjustment.objects.all()
    serializer_class = StockAdjustmentSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication,
    ]
    permission_classes = [InventoryPermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'product__name',
        'product__sku',
        'stock_take__reference_number',
        'reason',
    ]
    ordering_fields = [
        'created_at',
        'approved_at',
        'adjustment_quantity',
        'product__name',
    ]
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    # ----------------------------------
    # Queryset scoping (company-aware)
    # ----------------------------------

    def get_queryset(self):
        try:
            user = self.request.user
            if not user.is_authenticated:
                logger.warning("Unauthenticated access attempt to StockAdjustmentViewSet.")
                return StockAdjustment.objects.none()

            company = getattr(user, 'company', None) or (
                user if isinstance(user, Company) else None
            )

            identifier = (
                getattr(company, 'name', None)
                or getattr(company, 'username', None)
                or 'Unknown'
            )

            if not company:
                logger.warning(f"{identifier} has no associated company.")
                return StockAdjustment.objects.none()

            logger.info(
                f"{identifier} fetching stock adjustments for company "
                f"'{getattr(company, 'name', 'Unknown')}'."
            )

            return (
                StockAdjustment.objects
                .filter(stock_take__company=company)
                .select_related(
                    'product',
                    'stock_take',
                    'approved_by',
                )
            )

        except Exception as e:
            logger.error(e)
            return StockAdjustment.objects.none()

    # ----------------------------------
    # Create only (immutable resource)
    # ----------------------------------

    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (
            user if isinstance(user, Company) else None
        )

        adjustment = serializer.save(approved_by=user)

        identifier = (
            getattr(company, 'name', None)
            or getattr(company, 'username', None)
            or 'Unknown'
        )

        logger.success(
            f"StockAdjustment created for product '{adjustment.product.name}' "
            f"({adjustment.adjustment_quantity}) by {identifier}."
        )

    # ----------------------------------
    # Disable update & delete
    # ----------------------------------

    def update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Stock adjustments cannot be updated."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def partial_update(self, request, *args, **kwargs):
        return Response(
            {"detail": "Stock adjustments cannot be updated."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def destroy(self, request, *args, **kwargs):
        return Response(
            {"detail": "Stock adjustments cannot be deleted."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )