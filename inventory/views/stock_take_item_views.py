from rest_framework.viewsets import ModelViewSet
from inventory.models.stock_take_item_model import StockTakeItem
from inventory.serializers.stock_take_item_serializer import StockTakeItemSerializer
from inventory.permissions.inventory_permissions import InventoryPermission
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from company.models.company_model import Company
from rest_framework.filters import SearchFilter, OrderingFilter
from config.pagination.pagination import StandardResultsSetPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from inventory.services.stock_take_item_service import StockItemService
from inventory.models.product_model import Product
from inventory.models.stock_take_model import StockTake
from rest_framework import status
from django.db.models import Q
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


    @action(detail=False, methods=["post"], url_path="add-item")
    def add_item(self, request):
        """
        Adds or updates a stock take item using update_or_create logic.
        """
        stock_take_id = request.data.get("stock_take_id")
        product_id = request.data.get("product_id")
        expected_quantity = request.data.get("expected_quantity")
        counted_quantity = request.data.get("counted_quantity")

        if not stock_take_id or not product_id:
            return Response({"error": "stock_take_id and product_id are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            expected_quantity = int(expected_quantity)
            counted_quantity = int(counted_quantity)
        except (ValueError, TypeError):
            return Response({"error": "expected_quantity and counted_quantity must be integers."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            stock_take = StockTake.objects.get(id=stock_take_id)
            product = Product.objects.get(id=product_id)

            # Optional: ensure stock_take belongs to user's company
            company = getattr(request.user, 'company', None) or (request.user if isinstance(request.user, Company) else None)
            if stock_take.company != company:
                return Response({"error": "Stock take does not belong to your company."},
                                status=status.HTTP_403_FORBIDDEN)

            item = StockItemService.add_stock_take_item(
                stock_take=stock_take,
                product=product,
                expected_quantity=expected_quantity,
                counted_quantity=counted_quantity
            )

            serializer = self.get_serializer(item)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except (StockTake.DoesNotExist, Product.DoesNotExist):
            return Response({"error": "Stock take or product not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="update-counted")
    def update_counted(self, request, pk=None):
        """
        Update the counted quantity for a specific stock take item.
        """
        new_counted = request.data.get("counted_quantity")
        try:
            new_counted = int(new_counted)
        except (ValueError, TypeError):
            return Response({"error": "counted_quantity must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = self.get_object()
            updated_item = StockItemService.update_counted_quantity(item, new_counted)
            serializer = self.get_serializer(updated_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="update-expected")
    def update_expected(self, request, pk=None):
        """
        Update the expected quantity for a specific stock take item.
        """
        new_expected = request.data.get("expected_quantity")
        try:
            new_expected = int(new_expected)
        except (ValueError, TypeError):
            return Response({"error": "expected_quantity must be an integer."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = self.get_object()
            updated_item = StockItemService.update_expected_quantity(item, new_expected)
            serializer = self.get_serializer(updated_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

    @action(detail=False, methods=["get"], url_path="by-stock-take/(?P<stock_take_id>[^/.]+)")
    def by_stock_take(self, request, stock_take_id=None):
        """
        Retrieve all stock take items linked to a specific stock take.
        """
        try:
            stock_take = StockTake.objects.get(id=stock_take_id)
            company = getattr(request.user, 'company', None) or (request.user if isinstance(request.user, Company) else None)
            if stock_take.company != company:
                return Response({"error": "Stock take does not belong to your company."},
                                status=status.HTTP_403_FORBIDDEN)

            items = StockItemService.get_stock_take_items(stock_take)
            serializer = self.get_serializer(items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except StockTake.DoesNotExist:
            return Response({"error": "Stock take not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    
