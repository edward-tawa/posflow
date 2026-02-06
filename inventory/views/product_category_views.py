from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from inventory.models.product_category_model import ProductCategory
from inventory.serializers.product_category_serializer import ProductCategorySerializer
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from inventory.permissions.inventory_permissions import InventoryPermission
from rest_framework.filters import SearchFilter, OrderingFilter
from config.pagination.pagination import StandardResultsSetPagination
from config.utilities.get_queryset import get_company_queryset  # helper function
from company.models.company_model import Company
from django.db.models import Q
from rest_framework.decorators import action
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

    @action(detail=False, methods=['get'], url_path='list-by-branch')
    def list_by_branch(self, request):
        """
        List categories filtered by optional branch param, includes company-wide categories.
        GET param: ?branch=<branch_id>
        """
        branch_param = request.query_params.get('branch', None)
        user = request.user
        company_or_user = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)

        if not company_or_user:
            return Response({"error": "Company information is missing."}, status=status.HTTP_400_BAD_REQUEST)

        filters = Q(company=company_or_user)
        if branch_param:
            filters &= Q(branch=branch_param) | Q(branch__isnull=True)

        categories = ProductCategory.objects.filter(filters).order_by('name')
        serializer = ProductCategorySerializer(categories, many=True)
        logger.info(f"Listed {len(categories)} categories for company '{getattr(company_or_user, 'name', 'Unknown')}' with branch='{branch_param}'.")
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='search')
    def search(self, request):
        """
        Search categories by name with optional branch filter.
        GET params: ?q=<search_term>&branch=<branch_id>
        """
        search_term = request.query_params.get('q', '')
        branch_param = request.query_params.get('branch', None)
        user = request.user
        company_or_user = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)

        if not company_or_user:
            return Response({"error": "Company information is missing."}, status=status.HTTP_400_BAD_REQUEST)

        filters = Q(company=company_or_user) & Q(name__icontains=search_term)
        if branch_param:
            filters &= Q(branch=branch_param) | Q(branch__isnull=True)

        categories = ProductCategory.objects.filter(filters).order_by('name')
        serializer = ProductCategorySerializer(categories, many=True)
        logger.info(f"Searched categories with term '{search_term}' for company '{getattr(company_or_user, 'name', 'Unknown')}', branch='{branch_param}'. Found {len(categories)} results.")
        return Response(serializer.data, status=status.HTTP_200_OK)


# class ProductCategoryListView(APIView):
#     """
#     API view to list all product categories for a company/branch.
#     Includes company-wide categories if branch is specified.
#     """
#     authentication_classes = [CompanyCookieJWTAuthentication, UserCookieJWTAuthentication, JWTAuthentication]
#     permission_classes = [InventoryPermission]

#     def get(self, request, *args, **kwargs):
#         user = request.user
#         branch_param = request.query_params.get('branch', None)
#         company_or_user = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)

#         if not company_or_user:
#             return Response({"error": "Company information is missing."}, status=status.HTTP_400_BAD_REQUEST)

#         # Filter by branch if provided, include company-wide categories
#         filters = Q(company=company_or_user)
#         if branch_param:
#             filters &= Q(branch=branch_param) | Q(branch__isnull=True)

#         categories = ProductCategory.objects.filter(filters).order_by('name')
#         serializer = ProductCategorySerializer(categories, many=True)
#         logger.info(f"Listed {len(categories)} categories for company '{getattr(company_or_user, 'name', 'Unknown')}' with branch='{branch_param}'.")
#         return Response(serializer.data, status=status.HTTP_200_OK)


# class ProductCategorySearchView(APIView):
#     """
#     API view to search product categories by name within a company/branch.
#     Includes company-wide categories if branch is specified.
#     """
#     authentication_classes = [CompanyCookieJWTAuthentication, UserCookieJWTAuthentication, JWTAuthentication]
#     permission_classes = [InventoryPermission]

#     def get(self, request, *args, **kwargs):
#         search_term = request.query_params.get('q', '')
#         branch_param = request.query_params.get('branch', None)
#         user = request.user
#         company_or_user = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)

#         if not company_or_user:
#             return Response({"error": "Company information is missing."}, status=status.HTTP_400_BAD_REQUEST)

#         # Filter by branch if provided, include company-wide categories
#         filters = Q(company=company_or_user) & Q(name__icontains=search_term)
#         if branch_param:
#             filters &= Q(branch=branch_param) | Q(branch__isnull=True)

#         categories = ProductCategory.objects.filter(filters).order_by('name')
#         serializer = ProductCategorySerializer(categories, many=True)
#         logger.info(f"Searched categories with term '{search_term}' for company '{getattr(company_or_user, 'name', 'Unknown')}', branch='{branch_param}'. Found {len(categories)} results.")
#         return Response(serializer.data, status=status.HTTP_200_OK)
