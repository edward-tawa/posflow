from rest_framework.viewsets import ModelViewSet
from accounts.models.account_model import Account
from accounts.serializers.account_serializer import AccountSerializer
from rest_framework.permissions import IsAuthenticated
from config.auth.jwt_token_authentication import UserCookieJWTAuthentication, CompanyCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from config.utilities.pagination import StandardResultsSetPagination
from config.utilities.get_queryset import get_company_queryset
from accounts.permissions.account_permissions import AccountPermission
from company.models.company_model import Company
from loguru import logger


class AccountViewSet(ModelViewSet):
    """
    ViewSet for managing Accounts within a company.
    Provides CRUD operations with appropriate permissions and filtering.
    """
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [AccountPermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'account_type', 'number']
    ordering_fields = ['created_at', 'updated_at', 'name']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Return Account queryset filtered by the logged-in company/user."""
        return get_company_queryset(self.request, Account)

    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        account = serializer.save(company=company)
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(account_number=account.account_number).success(
            f"Account '{account.name}' (Number: {account.account_number}) created by {actor} in company '{getattr(company, 'name', 'Unknown')}'."
        )

    def perform_update(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        account = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(account_number=account.account_number).info(
            f"Account '{account.name}' (Number: {account.account_number}) updated by {actor}."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(account_number=instance.account_number).warning(
            f"Account '{instance.name}' (Number: {instance.account_number}) deleted by {actor}."
        )
        instance.delete()