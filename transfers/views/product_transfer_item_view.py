from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import status
from rest_framework.response import Response
from config.auth.jwt_token_authentication import UserCookieJWTAuthentication, CompanyCookieJWTAuthentication
from config.utilities.pagination import StandardResultsSetPagination
from config.utilities.get_logged_in_company import get_company_queryset
from transfers.models.product_transfer_item_model import ProductTransferItem
from transfers.serializers.product_transfer_item_serializer import ProductTransferItemSerializer
from config.permissions.company_role_base_permission import CompanyRolePermission
from company.models.company_model import Company
from loguru import logger

class ProductTransferItemViewSet(ModelViewSet):
    """
    ViewSet for managing Product Transfer Items within a company.
    Provides CRUD operations with appropriate permissions and filtering.
    """
    queryset = ProductTransferItem.objects.all()
    serializer_class = ProductTransferItemSerializer
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication]
    permission_classes = [CompanyRolePermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['product__name', 'transfer__reference_number']
    ordering_fields = ['created_at', 'updated_at', 'quantity']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return get_company_queryset(self.request, ProductTransferItem).selected_related(
            'product',
            'transfer',
        ).all()

    def perform_create(self, serializer):
        product_transfer_item = serializer.save()
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        identifier = getattr(company, 'name', None) or getattr(company, 'username', None) or 'Unknown'
        logger.bind(id=product_transfer_item.id).success(
            f"ProductTransferItem '{product_transfer_item.id}' created by {identifier} in company '{getattr(company, 'name', 'Unknown')}'."
        )

    def perform_update(self, serializer):
        product_transfer_item = serializer.save()
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        identifier = getattr(company, 'name', None) or getattr(company, 'username', None) or 'Unknown'
        logger.bind(id=product_transfer_item.id).info(
            f"ProductTransferItem '{product_transfer_item.id}' updated by {identifier}."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        identifier = getattr(company, 'name', None) or getattr(company, 'username', None) or 'Unknown'
        logger.bind(id=instance.id).warning(
            f"ProductTransferItem '{instance.id}' deleted by {identifier}."
        )
        instance.delete()