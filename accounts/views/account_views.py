from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from transactions.models.transaction_model import Transaction
from transactions.serializers.transaction_serializer import TransactionSerializer
from accounts.models.account_model import Account
from accounts.serializers.account_serializer import AccountSerializer
from rest_framework.permissions import IsAuthenticated
from config.auth.jwt_token_authentication import UserCookieJWTAuthentication, CompanyCookieJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from config.pagination.pagination import StandardResultsSetPagination
from config.utilities.get_queryset import get_company_queryset
from accounts.permissions.account_permissions import AccountPermission
from accounts.services.accounts_service import AccountsService
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
        try:
            """Return Account queryset filtered by the logged-in company/user."""
            return get_company_queryset(self.request, Account)
        except Exception as e:
            return self.queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        account = serializer.save()
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


class GetAccountTransactions(APIView):
    """
    API View to retrieve transactions for a specific account.
    """
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [AccountPermission, IsAuthenticated]

    def get(self, request, account_id):
        try:
            account = Account.objects.get(id=account_id)
        except Account.DoesNotExist:
            logger.warning(f"Account with ID {account_id} does not exist.")
            return Response({"detail": "Account not found."}, status=status.HTTP_404_NOT_FOUND)

        if not AccountPermission().has_object_permission(request, self, account):
            logger.warning(f"Unauthorized access attempt to Account ID {account_id} by user {request.user}.")
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        transactions = AccountsService.get_account_transactions(account)
        serializer = TransactionSerializer(transactions, many=True)
        logger.info(f"Retrieved {len(transactions)} transactions for Account ID {account_id} by user {request.user}.")
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class GetAccountBalance(APIView):
    """
    API View to retrieve the balance of a specific account.
    """
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [AccountPermission, IsAuthenticated]

    def get(self, request, account_id):
        try:
            account = Account.objects.get(id=account_id)
        except Account.DoesNotExist:
            logger.warning(f"Account with ID {account_id} does not exist.")
            return Response({"detail": "Account not found."}, status=status.HTTP_404_NOT_FOUND)

        if not AccountPermission().has_object_permission(request, self, account):
            logger.warning(f"Unauthorized access attempt to Account ID {account_id} by user {request.user}.")
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        balance = account.balance
        logger.info(f"Retrieved balance for Account ID {account_id} by user {request.user}: {balance}")
        return Response({"account_id": account_id, "balance": balance}, status=status.HTTP_200_OK)
    


class FreezeAccount(APIView):
    """
    API View to freeze a specific account.
    """
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [AccountPermission, IsAuthenticated]

    def post(self, request, account_id):
        try:
            account = Account.objects.get(id=account_id)
        except Account.DoesNotExist:
            logger.warning(f"Account with ID {account_id} does not exist.")
            return Response({"detail": "Account not found."}, status=status.HTTP_404_NOT_FOUND)

        if not AccountPermission().has_object_permission(request, self, account):
            logger.warning(f"Unauthorized freeze attempt on Account ID {account_id} by user {request.user}.")
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        account.is_frozen = True
        account.save(update_fields=['is_frozen'])
        logger.info(f"Account ID {account_id} frozen by user {request.user}.")
        return Response({"detail": f"Account {account_id} has been frozen."}, status=status.HTTP_200_OK)
    


class UnfreezeAccount(APIView):
    """
    API View to unfreeze a specific account.
    """
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [AccountPermission, IsAuthenticated]

    def post(self, request, account_id):
        try:
            account = Account.objects.get(id=account_id)
        except Account.DoesNotExist:
            logger.warning(f"Account with ID {account_id} does not exist.")
            return Response({"detail": "Account not found."}, status=status.HTTP_404_NOT_FOUND)

        if not AccountPermission().has_object_permission(request, self, account):
            logger.warning(f"Unauthorized unfreeze attempt on Account ID {account_id} by user {request.user}.")
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        if AccountsService.unfreeze_account(account):
            logger.info(f"Account ID {account_id} unfrozen by user {request.user}.")
            return Response({"detail": f"Account {account_id} has been unfrozen."}, status=status.HTTP_200_OK)
        return Response({"detail": f"Failed to unfreeze account {account_id}."}, status=status.HTTP_400_BAD_REQUEST)
