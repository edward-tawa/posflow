from rest_framework.viewsets import ModelViewSet
from accounts.models.sales_account_model import SalesAccount
from accounts.serializers.sales_account_serializer import SalesAccountSerializer
from rest_framework.permissions import IsAuthenticated
from config.auth.jwt_token_authentication import UserCookieJWTAuthentication, CompanyCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from config.pagination.pagination import StandardResultsSetPagination
from config.utilities.get_queryset import get_account_company_queryset
from accounts.permissions.account_permission import AccountPermissionAccess
from company.models.company_model import Company
from loguru import logger

class SalesAccountViewSet(ModelViewSet):
    """
    ViewSet for managing Sales Accounts within a company.
    Provides CRUD operations with appropriate permissions and filtering.
    """
    queryset = SalesAccount.objects.all()
    serializer_class = SalesAccountSerializer
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [AccountPermissionAccess]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['account__name', 'account__account_number', 'customer__first_name', 'sales_person__username']
    ordering_fields = ['created_at', 'updated_at', 'account__name', 'customer__first_name']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """Return SalesAccount queryset filtered by the logged-in company/user."""
            return get_account_company_queryset(self.request, SalesAccount).select_related('account', 'branch', 'customer', 'sales_person')
        except Exception as e:
            return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        sales_account = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(account_number=sales_account.account.account_number, customer=sales_account.customer_id).success(
            f"SalesAccount for account '{sales_account.account.name}' (Number: {sales_account.account.account_number}) "
            f"and customer ID '{sales_account.customer_id}' created by {actor} in company '{getattr(company, 'name', 'Unknown')}'."
        )

    def perform_update(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        sales_account = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(account_number=sales_account.account.account_number, customer=sales_account.customer_id).info(
            f"SalesAccount for account '{sales_account.account.name}' (Number: {sales_account.account.account_number}) "
            f"and customer ID '{sales_account.customer_id}' updated by {actor}."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(account_number=instance.account.account_number, customer=instance.customer_id).warning(
            f"SalesAccount for account '{instance.account.name}' (Number: {instance.account.account_number}) "
            f"and customer ID '{instance.customer_id}' deleted by {actor}."
        )
        instance.delete()
