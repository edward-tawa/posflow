from rest_framework.viewsets import ModelViewSet
from accounts.models.cash_account_model import CashAccount
from accounts.serializers.cash_account_serializer import CashAccountSerializer
from rest_framework.permissions import IsAuthenticated
from config.auth.jwt_token_authentication import UserCookieJWTAuthentication, CompanyCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from config.pagination.pagination import StandardResultsSetPagination
from config.utilities.get_queryset import get_account_company_queryset
from accounts.permissions.account_permission import AccountPermissionAccess
from company.models.company_model import Company
from loguru import logger

class CashAccountViewSet(ModelViewSet):
    """
    ViewSet for managing Cash Accounts within a company.
    Provides CRUD operations with appropriate permissions and filtering.
    """
    queryset = CashAccount.objects.all()
    serializer_class = CashAccountSerializer
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [AccountPermissionAccess]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['account__name', 'account__account_number']
    ordering_fields = ['created_at', 'updated_at', 'account__name']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """Return CashAccount queryset filtered by the logged-in company/user."""
            return get_account_company_queryset(self.request, CashAccount).select_related('account', 'branch')
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        cash_account = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(account_number=cash_account.account.account_number).success(
            f"CashAccount for account '{cash_account.account.name}' (Number: {cash_account.account.account_number}) "
            f"created by {actor} in company '{getattr(company, 'name', 'Unknown')}'."
        )

    def perform_update(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        cash_account = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(account_number=cash_account.account.account_number).info(
            f"CashAccount for account '{cash_account.account.name}' (Number: {cash_account.account.account_number}) updated by {actor}."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(account_number=instance.account.account_number).warning(
            f"CashAccount for account '{instance.account.name}' (Number: {instance.account.account_number}) deleted by {actor}."
        )
        instance.delete()
