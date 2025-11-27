from rest_framework.viewsets import ModelViewSet
from accounts.models.branch_account_model import BranchAccount
from accounts.serializers.branch_account_serializer import BranchAccountSerializer
from rest_framework.permissions import IsAuthenticated
from config.auth.jwt_token_authentication import UserCookieJWTAuthentication, CompanyCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from config.utilities.pagination import StandardResultsSetPagination
from config.utilities.get_queryset import get_company_queryset
from accounts.permissions.account_permissions import AccountPermission
from company.models.company_model import Company
from loguru import logger

class BranchAccountViewSet(ModelViewSet):
    """
    ViewSet for managing Branch Accounts within a company.
    Provides CRUD operations with appropriate permissions and filtering.
    """
    queryset = BranchAccount.objects.all()
    serializer_class = BranchAccountSerializer
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [AccountPermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['branch__name', 'account__name', 'account__number']
    ordering_fields = ['created_at', 'updated_at', 'branch__name']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Return BranchAccount queryset filtered by the logged-in company/user."""
        return get_company_queryset(self.request, BranchAccount).select_related('branch', 'account')
    
    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        branch_account = serializer.save(company=company)
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(branch=branch_account.branch.name, account_number=branch_account.account.account_number).success(
            f"BranchAccount for branch '{branch_account.branch.name}' and account '{branch_account.account.name}' (Number: {branch_account.account.account_number}) created by {actor} in company '{getattr(company, 'name', 'Unknown')}'."
        )
    
    def perform_update(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        branch_account = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(branch=branch_account.branch.name, account_number=branch_account.account.number).info(
            f"BranchAccount for branch '{branch_account.branch.name}' and account '{branch_account.account.name}' (Number: {branch_account.account.number}) updated by {actor}."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(branch=instance.branch.name, account_number=instance.account.number).warning(
            f"BranchAccount for branch '{instance.branch.name}' and account '{instance.account.name}' (Number: {instance.account.number}) deleted by {actor}."
        )
        instance.delete()