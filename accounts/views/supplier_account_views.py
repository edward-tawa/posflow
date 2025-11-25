from rest_framework.viewsets import ModelViewSet
from accounts.models.supplier_account import SupplierAccount
from accounts.serializers.supplier_account_serializer import SupplierAccountSerializer
from rest_framework.permissions import IsAuthenticated
from config.auth.jwt_token_authentication import UserCookieJWTAuthentication, CompanyCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from config.utilities.pagination import StandardResultsSetPagination
from config.utilities.get_queryset import get_company_queryset
from accounts.permissions.account_permissions import AccountPermission
from company.models.company_model import Company
from loguru import logger


class SupplierAccountViewSet(ModelViewSet):
    """
    ViewSet for managing Supplier Accounts within a company.
    Provides CRUD operations with appropriate permissions and filtering.
    """
    queryset = SupplierAccount.objects.all()
    serializer_class = SupplierAccountSerializer
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [AccountPermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['supplier__name', 'account__name', 'account__number']
    ordering_fields = ['created_at', 'updated_at', 'supplier__name']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Return SupplierAccount queryset filtered by the logged-in company/user."""
        return get_company_queryset(self.request, SupplierAccount).select_related('supplier', 'account')
    
    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        supplier_account = serializer.save(company=company)
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(supplier=supplier_account.supplier.name, account_number=supplier_account.account.number).success(
            f"SupplierAccount for supplier '{supplier_account.supplier.name}' and account '{supplier_account.account.name}' (Number: {supplier_account.account.number}) created by {actor} in company '{getattr(company, 'name', 'Unknown')}'."
        )
    
    def perform_update(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        supplier_account = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(supplier=supplier_account.supplier.name, account_number=supplier_account.account.number).info(
            f"SupplierAccount for supplier '{supplier_account.supplier.name}' and account '{supplier_account.account.name}' (Number: {supplier_account.account.number}) updated by {actor}."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(supplier=instance.supplier.name, account_number=instance.account.number).warning(
            f"SupplierAccount for supplier '{instance.supplier.name}' and account '{instance.account.name}' (Number: {instance.account.number}) deleted by {actor}."
        )
        instance.delete()