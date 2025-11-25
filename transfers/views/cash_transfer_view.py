from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import status
from rest_framework.response import Response
from config.auth.jwt_token_authentication import UserCookieJWTAuthentication, CompanyCookieJWTAuthentication
from config.utilities.pagination import StandardResultsSetPagination
from config.utilities.get_logged_in_company import get_company_queryset
from transfers.models.cash_transfer_model import CashTransfer
from transfers.serializers.cash_transfer_serializer import CashTransferSerializer
from config.permissions.company_role_base_permission import CompanyRolePermission
from company.models.company_model import Company
from loguru import logger



class CashTransferViewSet(ModelViewSet):
    """
    ViewSet for managing Cash Transfers within a company.
    Provides CRUD operations with approopriate permissions and filtering.
    """
    queryset = CashTransfer.objects.all()
    serializer_class = CashTransferSerializer
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication]
    permission_classes = [CompanyRolePermission]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['reference_number', 'transfer_date', 'source_branch__name', 'destination_branch__name', 'status']
    ordering_fields = ['transfer_date', 'created_at', 'updated_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return get_company_queryset(self.request, CashTransfer).select_related(
                    'transfer',
                    'source_branch',
                    'destination_branch',
                    'source_branch_account',
                    'destination_branch_account'
                    ).all()

    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        cash_transfer = serializer.save(company=company)
        identifier = getattr(company, 'name', None) or getattr(company, 'username', None) or 'Unknown'
        logger.bind(reference_number=cash_transfer.reference_number).success(
            f"CashTransfer '{cash_transfer.reference_number}' created by {identifier} in company '{getattr(company, 'name', 'Unknown')}'."
        )

    def perform_update(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        cash_transfer = serializer.save()
        identifier = getattr(company, 'name', None) or getattr(company, 'username', None) or 'Unknown'
        logger.bind(reference_number=cash_transfer.reference_number).info(
            f"CashTransfer '{cash_transfer.reference_number}' updated by {identifier}."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        identifier = getattr(company, 'name', None) or getattr(company, 'username', None) or 'Unknown'
        logger.bind(reference_number=instance.reference_number).warning(
            f"CashTransfer '{instance.reference_number}' deleted by {identifier}."
        )
        instance.delete()