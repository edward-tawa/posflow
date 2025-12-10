from rest_framework.viewsets import ModelViewSet
from accounts.models.purchases_returns_account_model import PurchasesReturnsAccount
from accounts.serializers.purchases_returns_account_serializer import PurchasesReturnsAccountSerializer
from rest_framework.permissions import IsAuthenticated
from config.auth.jwt_token_authentication import UserCookieJWTAuthentication, CompanyCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from config.pagination.pagination import StandardResultsSetPagination
from config.utilities.get_queryset import get_company_queryset
from accounts.permissions.account_permissions import AccountPermission
from company.models.company_model import Company
from loguru import logger

class PurchasesReturnsAccountViewSet(ModelViewSet):
    """
    ViewSet for managing Purchases Returns Accounts within a company.
    Provides CRUD operations with appropriate permissions and filtering.
    """
    queryset = PurchasesReturnsAccount.objects.all()
    serializer_class = PurchasesReturnsAccountSerializer
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [AccountPermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['account__name', 'account__account_number', 'supplier__name', 'return_person__username']
    ordering_fields = ['created_at', 'updated_at', 'account__name', 'supplier__name']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """Return PurchasesReturnsAccount queryset filtered by the logged-in company/user."""
            return get_company_queryset(self.request, PurchasesReturnsAccount).select_related('account', 'branch', 'supplier', 'return_person')
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        purchases_returns_account = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(account_number=purchases_returns_account.account.account_number, supplier=purchases_returns_account.supplier_id).success(
            f"PurchasesReturnsAccount for account '{purchases_returns_account.account.name}' (Number: {purchases_returns_account.account.account_number}) "
            f"and supplier ID '{purchases_returns_account.supplier_id}' created by {actor} in company '{getattr(company, 'name', 'Unknown')}'."
        )

    def perform_update(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        purchases_returns_account = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(account_number=purchases_returns_account.account.account_number, supplier=purchases_returns_account.supplier_id).info(
            f"PurchasesReturnsAccount for account '{purchases_returns_account.account.name}' (Number: {purchases_returns_account.account.account_number}) "
            f"and supplier ID '{purchases_returns_account.supplier_id}' updated by {actor}."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(account_number=instance.account.account_number, supplier=instance.supplier_id).warning(
            f"PurchasesReturnsAccount for account '{instance.account.name}' (Number: {instance.account.account_number}) "
            f"and supplier ID '{instance.supplier_id}' deleted by {actor}."
        )
        instance.delete()
