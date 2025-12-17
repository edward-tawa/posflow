from rest_framework.viewsets import ModelViewSet
from accounts.models.bank_account_model import BankAccount
from accounts.serializers.bank_account_serializer import BankAccountSerializer
from rest_framework.permissions import IsAuthenticated
from config.auth.jwt_token_authentication import UserCookieJWTAuthentication, CompanyCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from config.pagination.pagination import StandardResultsSetPagination
from config.utilities.get_queryset import get_company_queryset
from accounts.permissions.account_permission import AccountPermissionAccess
from company.models.company_model import Company
from rest_framework.response import Response
from rest_framework import status
from loguru import logger

class BankAccountViewSet(ModelViewSet):
    """
    ViewSet for managing Bank Accounts within a company.
    Provides CRUD operations with appropriate permissions and filtering.
    """
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [AccountPermissionAccess]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['account__name', 'account__account_number', 'bank_name']
    ordering_fields = ['created_at', 'updated_at', 'account__name']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """Return BankAccount queryset filtered by the logged-in company/user."""
            return get_company_queryset(self.request, BankAccount).select_related('account', 'branch')
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        bank_account = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(account_number=bank_account.account.account_number, bank_name=bank_account.bank_name).success(
            f"BankAccount for account '{bank_account.account.name}' (Number: {bank_account.account.account_number}, Bank: {bank_account.bank_name}) "
            f"created by {actor} in company '{getattr(company, 'name', 'Unknown')}'."
        )

    def perform_update(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        bank_account = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(account_number=bank_account.account.account_number, bank_name=bank_account.bank_name).info(
            f"BankAccount for account '{bank_account.account.name}' (Number: {bank_account.account.account_number}, Bank: {bank_account.bank_name}) updated by {actor}."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(account_number=instance.account.account_number, bank_name=instance.bank_name).warning(
            f"BankAccount for account '{instance.account.name}' (Number: {instance.account.account_number}, Bank: {instance.bank_name}) deleted by {actor}."
        )
        instance.delete()
