from rest_framework.viewsets import ModelViewSet
from accounts.models.expense_account_model import ExpenseAccount
from accounts.serializers.expense_account_serializer import ExpenseAccountSerializer
from rest_framework.permissions import IsAuthenticated
from config.auth.jwt_token_authentication import UserCookieJWTAuthentication, CompanyCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from config.pagination.pagination import StandardResultsSetPagination
from config.utilities.get_queryset import get_company_queryset
from accounts.permissions.account_permissions import AccountPermission
from company.models.company_model import Company
from loguru import logger

class ExpenseAccountViewSet(ModelViewSet):
    """
    ViewSet for managing Expense Accounts within a company.
    Provides CRUD operations with appropriate permissions and filtering.
    """
    queryset = ExpenseAccount.objects.all()
    serializer_class = ExpenseAccountSerializer
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [AccountPermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['account__name', 'account__account_number', 'expense_category__name', 'paid_by__username']
    ordering_fields = ['created_at', 'updated_at', 'account__name', 'expense_category__name']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """Return ExpenseAccount queryset filtered by the logged-in company/user."""
            return get_company_queryset(self.request, ExpenseAccount).select_related('account', 'branch', 'expense', 'paid_by')
        except Exception as e:
            logger.error(f"Error: {e}")
            return self.queryset.none()
        
    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        expense_account = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(account_number=expense_account.account.account_number, expense_category=expense_account.expense_category_id).success(
            f"ExpenseAccount for account '{expense_account.account.name}' (Number: {expense_account.account.account_number}) "
            f"and expense category ID '{expense_account.expense_category_id}' created by {actor} in company '{getattr(company, 'name', 'Unknown')}'."
        )

    def perform_update(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        expense_account = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(account_number=expense_account.account.account_number, expense_category=expense_account.expense_category_id).info(
            f"ExpenseAccount for account '{expense_account.account.name}' (Number: {expense_account.account.account_number}) "
            f"and expense category ID '{expense_account.expense_category_id}' updated by {actor}."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(account_number=instance.account.account_number, expense_category=instance.expense_category_id).warning(
            f"ExpenseAccount for account '{instance.account.name}' (Number: {instance.account.account_number}) "
            f"and expense category ID '{instance.expense_category_id}' deleted by {actor}."
        )
        instance.delete()
