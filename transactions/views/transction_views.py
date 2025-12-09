from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from transactions.permissions.transaction_permissions import TransactionPermissions
from config.pagination.pagination import StandardResultsSetPagination
from transactions.models import Transaction
from transactions.serializers.transaction_serializer import TransactionSerializer
from accounts.models.account_model import Account
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from transactions.services.transcation_service import TransactionService
from loguru import logger


class TransactionViewSet(ModelViewSet):
    """
    ViewSet for managing Transactions.
    Supports listing, retrieving, creating, updating, and deleting transactions.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [TransactionPermissions]  # Add your custom permissions

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'transaction_number',
        'transaction_type',
        'company__name',
        'branch__name'
    ]
    ordering_fields = ['created_at', 'updated_at', 'transaction_date', 'total_amount']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            Returns the Transaction queryset filtered by the logged-in company/user.
            """
            return (
                get_company_queryset(self.request, Transaction)
                .select_related('company', 'branch')
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {e}"

    def perform_create(self, serializer):
        """
        Saves a new Transaction instance and logs the event.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        transaction = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"Transaction '{transaction.transaction_number}' created by '{actor}' "
            f"for company '{transaction.company.name}'."
        )

    def perform_update(self, serializer):
        """
        Saves an updated Transaction instance and logs the event.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        transaction = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"Transaction '{transaction.transaction_number}' updated by '{actor}' "
            f"for company '{transaction.company.name}'."
        )

    def perform_destroy(self, instance):
        """
        Deletes a Transaction instance and logs the event.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        transaction_number = instance.transaction_number
        instance.delete()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.warning(
            f"Transaction '{transaction_number}' deleted by '{actor}' "
            f"from company '{company.name}'."
        )



