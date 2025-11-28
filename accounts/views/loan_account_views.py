from rest_framework.viewsets import ModelViewSet
from accounts.models.loan_account_model import LoanAccount
from accounts.serializers.loan_account_serializer import LoanAccountSerializer
from rest_framework.permissions import IsAuthenticated
from config.auth.jwt_token_authentication import UserCookieJWTAuthentication, CompanyCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from config.utilities.pagination import StandardResultsSetPagination
from config.utilities.get_queryset import get_company_queryset
from accounts.permissions.account_permissions import AccountPermission
from company.models.company_model import Company
from loguru import logger


class LoanAccountViewSet(ModelViewSet):
    """
    ViewSet for managing Loan Accounts within a company.
    Provides CRUD operations with appropriate permissions and filtering.
    """
    queryset = LoanAccount.objects.all()
    serializer_class = LoanAccountSerializer
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [AccountPermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['loan__name', 'account__name', 'account__number']
    ordering_fields = ['created_at', 'updated_at', 'loan__name']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Return LoanAccount queryset filtered by the logged-in company/user."""
        return get_company_queryset(self.request, LoanAccount).select_related('loan', 'account')
    
    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        loan_account = serializer.save(company=company)
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(loan=loan_account.loan.borrower.first_name, account_number=loan_account.account.account_number).success(
            f"LoanAccount for loan '{loan_account.loan.borrower.first_name}' and account '{loan_account.account.name}' (Number: {loan_account.account.account_number}) created by {actor} in company '{getattr(company, 'name', 'Unknown')}'."
        )
    
    def perform_update(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        loan_account = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(loan=loan_account.loan.name, account_number=loan_account.account.number).info(
            f"LoanAccount for loan '{loan_account.loan.name}' and account '{loan_account.account.name}' (Number: {loan_account.account.number}) updated by {actor}."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(loan=instance.loan.name, account_number=instance.account.number).warning(
            f"LoanAccount for loan '{instance.loan.name}' and account '{instance.account.name}' (Number: {instance.account.number}) deleted by {actor}."
        )
        instance.delete()