from rest_framework.viewsets import ModelViewSet
from inventory.models.product_model import Product
from inventory.serializers.product_serializer import ProductSerializer
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from inventory.permissions.inventory_permissions import InventoryPermission
from rest_framework.filters import SearchFilter, OrderingFilter
from config.pagination.pagination import StandardResultsSetPagination
from company.models.company_model import Company
from loguru import logger
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from inventory.services.product.product_service import ProductService
from inventory.models.product_category_model import ProductCategory
from inventory.serializers.adjust_stock_serializer import AdjustStockSerializer
from io import BytesIO


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
        try:
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
            return Product.objects.filter(company=company).select_related('product_category', 'company')
        except Exception as e:
            logger.error(e)
            return self.queryset.none()

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
    

    @action(detail=False, methods=['get'], url_path='list-by-category')
    def list_by_category(self, request):
        """
        List all products under a given category.
        GET param: ?category=<category_id>
        """
        category_id = request.query_params.get('category')
        if not category_id:
            return Response({"error": "Category ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            category = ProductCategory.objects.get(id=category_id)
        except ProductCategory.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

        products = ProductService.list_products_by_category(category)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    

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

        logger.info(f"Adjusted stock for Product '{product.name}' by {adjustment}. New quantity: {product.stock}")
        return Response({
            "id": product.id,
            "name": product.name,
            "new_stock_quantity": product.stock
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """
        Search products by name or description.
        GET param: ?q=<search_term>
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response({"error": "Search term is required"}, status=status.HTTP_400_BAD_REQUEST)

        company = getattr(request.user, 'company', None) or (request.user if isinstance(request.user, Company) else None)
        if not company:
            return Response({"error": "Company information missing"}, status=status.HTTP_400_BAD_REQUEST)

        products = ProductService.search_products(company, query)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='bulk-import')
    def bulk_import(self, request):
        """
        Bulk import products from CSV file.
        POST: multipart/form-data with 'file' field
        """
        csv_file = request.FILES.get('file')
        if not csv_file:
            return Response({"error": "CSV file is required"}, status=status.HTTP_400_BAD_REQUEST)

        company = getattr(request.user, 'company', None) or (request.user if isinstance(request.user, Company) else None)
        products, failed_rows = ProductService.bulk_import_products(company, csv_file)
        serializer = self.get_serializer(products, many=True)
        return Response({
            "imported": serializer.data,
            "failed_rows": failed_rows
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='bulk-export')
    def bulk_export(self, request):
        """
        Bulk export products to CSV.
        GET param: ?branch=<branch_id> (optional)
        """
        branch_param = request.query_params.get('branch', None)
        company = getattr(request.user, 'company', None) or (request.user if isinstance(request.user, Company) else None)
        response = ProductService.bulk_export_products(company, branch_param)
        response['Content-Disposition'] = 'attachment; filename="products.csv"'
        return response
    

    
    


    
