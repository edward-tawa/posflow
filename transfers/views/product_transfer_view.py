from rest_framework.viewsets import ModelViewSet
from transfers.models.product_transfer_model import ProductTransfer
from transfers.serializers.product_transfer_serializer import ProductTransferSerializer
from config.permissions.company_role_base_permission import CompanyRolePermission
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from transfers.django_filters.product_transfer_filters import ProductTransferFilter
from rest_framework import status
from rest_framework.response import Response
from company.models.company_model import Company
from config.utilities.pagination import StandardResultsSetPagination
from config.auth.jwt_token_authentication import UserCookieJWTAuthentication, CompanyCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from loguru import logger


class ProductTransferViewSet(ModelViewSet):
    """
    ViewSet for managing Product Transfers within a company.
    Provides CRUD operations with appropriate permissions and filtering.
    """
    queryset = ProductTransfer.objects.all()
    serializer_class = ProductTransferSerializer
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication]
    permission_classes = [CompanyRolePermission]
    
    # Correct filter setup
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    filterset_class = ProductTransferFilter
    
    search_fields = ['transfer__reference_number', 'transfer__transfer_date', 'source_branch__name', 'destination_branch__name', 'transfer__status']
    ordering_fields = ['transfer__transfer_date', 'created_at', 'updated_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return get_company_queryset(self.request, ProductTransfer).select_related(
            'transfer',
            'source_branch',
            'destination_branch'
        ).all()
    
    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        product_transfer = serializer.save(company=company)
        identifier = getattr(company, 'name', None) or getattr(company, 'username', None) or 'Unknown'
        logger.bind(reference_number=product_transfer.reference_number).success(
            f"ProductTransfer '{product_transfer.reference_number}' created by {identifier} in company '{getattr(company, 'name', 'Unknown')}'."
        )

    def perform_update(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        product_transfer = serializer.save()
        identifier = getattr(company, 'name', None) or getattr(company, 'username', None) or 'Unknown'
        logger.bind(reference_number=product_transfer.reference_number).info(
            f"ProductTransfer '{product_transfer.reference_number}' updated by {identifier}."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        identifier = getattr(company, 'name', None) or getattr(company, 'username', None) or 'Unknown'
        logger.bind(reference_number=instance.reference_number).warning(
            f"ProductTransfer '{instance.reference_number}' deleted by {identifier}."
        )
        instance.delete()
