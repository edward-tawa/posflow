from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import UserCookieJWTAuthentication, CompanyCookieJWTAuthentication
from config.pagination.pagination import StandardResultsSetPagination
from config.utilities.get_queryset import get_account_company_queryset
from accounts.permissions.account_permission import AccountPermissionAccess
from company.models.company_model import Company
from loguru import logger
from accounts.models.writeoff_account_model import WriteOffAccount
from accounts.serializers.writeoff_account_serializer import WriteOffAccountSerializer



class WriteOffAccountViewSet(ModelViewSet):
    """
    ViewSet for managing Write-Off Accounts within a company.
    Provides CRUD operations with appropriate permissions and filtering.
    """
    queryset = WriteOffAccount.objects.all()
    serializer_class = WriteOffAccountSerializer
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [AccountPermissionAccess]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['account__name', 'account_name', 'write_off__reference']
    ordering_fields = ['created_at', 'updated_at', 'account__name']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination


    def get_queryset(self):
        try:
            """Return WriteOffAccount queryset filtered by the logged-in company/user."""
            return get_account_company_queryset(self.request, WriteOffAccount).select_related(
                'account', 'write_off', 'product', 'company', 'branch'
            )
        except Exception as e:
            logger.error(f"Error fetching WriteOffAccount queryset: {e}")
            return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        writeoff_account = serializer.save(company=company)  # Assign company automatically
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(
            account=writeoff_account.account.name,
            write_off=writeoff_account.write_off.reference
        ).success(
            f"WriteOffAccount '{writeoff_account.account_name}' for Write-Off '{writeoff_account.write_off.reference}' "
            f"created by {actor} in company '{getattr(company, 'name', 'Unknown')}'."
        )

    def perform_update(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        writeoff_account = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(
            account=writeoff_account.account.name,
            write_off=writeoff_account.write_off.reference
        ).info(
            f"WriteOffAccount '{writeoff_account.account_name}' for Write-Off '{writeoff_account.write_off.reference}' "
            f"updated by {actor}."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(
            account=instance.account.name,
            write_off=instance.write_off.reference
        ).warning(
            f"WriteOffAccount '{instance.account_name}' for Write-Off '{instance.write_off.reference}' "
            f"deleted by {actor}."
        )
        instance.delete()