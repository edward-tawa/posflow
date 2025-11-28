from rest_framework.viewsets import ModelViewSet
from accounts.models.customer_account import CustomerAccount
from accounts.serializers.customer_account_serializer import CustomerAccountSerializer
from rest_framework.permissions import IsAuthenticated
from config.auth.jwt_token_authentication import UserCookieJWTAuthentication, CompanyCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from config.utilities.pagination import StandardResultsSetPagination
from config.utilities.get_queryset import get_company_queryset
from accounts.permissions.account_permissions import AccountPermission
from company.models.company_model import Company
from loguru import logger


class CustomerAccountViewSet(ModelViewSet):
    """
    ViewSet for managing Customer Accounts within a company.
    Provides CRUD operations with appropriate permissions and filtering.
    """
    queryset = CustomerAccount.objects.all()
    serializer_class = CustomerAccountSerializer
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [AccountPermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['customer__first_name', 'account__name', 'account__number']
    ordering_fields = ['created_at', 'updated_at', 'customer__first_name']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Return CustomerAccount queryset filtered by the logged-in company/user."""
        return get_company_queryset(self.request, CustomerAccount).select_related('customer', 'account')
    
    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        customer_account = serializer.save(company=company)
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(customer=customer_account.customer.first_name, account_number=customer_account.account.account_number).success(
            f"CustomerAccount for customer '{customer_account.customer.first_name}' and account '{customer_account.account.name}' (Number: {customer_account.account.account_number}) created by {actor} in company '{getattr(company, 'name', 'Unknown')}'."
        )
    
    def perform_update(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        customer_account = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(customer=customer_account.customer.name, account_number=customer_account.account.number).info(
            f"CustomerAccount for customer '{customer_account.customer.name}' and account '{customer_account.account.name}' (Number: {customer_account.account.number}) updated by {actor}."
        )
        
    def perform_destroy(self, instance):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(customer=instance.customer.name, account_number=instance.account.number).warning(
            f"CustomerAccount for customer '{instance.customer.name}' and account '{instance.account.name}' (Number: {instance.account.number}) deleted by {actor}."
        )
        instance.delete()