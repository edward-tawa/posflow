from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from inventory.models.product_stock_model import ProductStock
from inventory.serializers.product_stock_serializer import ProductStockSerializer
from inventory.permissions.inventory_permissions import InventoryPermission
from inventory.django_filters.product_stock_filter import ProductStockFilter
from inventory.serializers.adjust_stock_serializer import AdjustStockSerializer
from rest_framework.decorators import action
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
        try:
            """Return ProductStock queryset filtered by the logged-in company/user."""
            return get_company_queryset(self.request, ProductStock)
        except Exception as e:
            logger.error(e)
            return self.queryset.none()

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

    @action(detail=True, methods=['post'], url_path='adjust-stock')
    def adjust_stock(self, request, pk=None):
        """
        Adjust the stock quantity of a single product.
        POST payload: {"adjustment": <int>}
        """
        product = self.get_object()  # ensures detail=True, fetches by pk
        serializer = AdjustStockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        adjustment = serializer.validated_data['adjustment']
        product = ProductService.adjust_product_quantity(product, adjustment)

        logger.info(f"Adjusted stock for Product '{product.name}' by {adjustment}. New quantity: {product.stock_quantity}")
        return Response({
            "id": product.id,
            "name": product.name,
            "new_stock_quantity": product.stock_quantity
        }, status=status.HTTP_200_OK)
    

    @action(detail=True, methods=['post'], url_path='add')
    def add_stock(self, request, pk=None):
        product_stock = self.get_object()
        qty = int(request.data.get("quantity", 0))
        company = get_logged_in_company(request)

        updated = ProductStockService.add_stock(
            product_stock.product, company, product_stock.branch, qty
        )

        return Response({
            "message": "Stock added",
            "new_quantity": updated.quantity
        })
    

    @action(detail=True, methods=['post'], url_path='remove')
    def remove_stock(self, request, pk=None):
        product_stock = self.get_object()
        qty = int(request.data.get("quantity", 0))
        company = get_logged_in_company(request)

        updated = ProductStockService.remove_stock(
            product_stock.product, company, product_stock.branch, qty
        )

        return Response({
            "message": "Stock removed",
            "new_quantity": updated.quantity
        })
    


    @action(detail=True, methods=['get'], url_path='check')
    def check_stock(self, request, pk=None):
        product_stock = self.get_object()
        company = get_logged_in_company(request)

        total = ProductStockService.check_product_stock(
            product_stock.product, company, product_stock.branch
        )

        return Response({
            "product": product_stock.product.name,
            "branch": product_stock.branch.name,
            "quantity": total
        })
    

    @action(detail=True, methods=['get'], url_path='value')
    def total_stock_value(self, request, pk=None):
        product_stock = self.get_object()

        value = ProductStockService.calculate_total_product_stock_value(
            product_stock.product,
            product_stock.branch
        )

        return Response({
            "product": product_stock.product.name,
            "branch": product_stock.branch.name,
            "total_value": value
        })

