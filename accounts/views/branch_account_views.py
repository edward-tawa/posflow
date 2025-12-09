from rest_framework.viewsets import ModelViewSet
from accounts.models.branch_account_model import BranchAccount
from accounts.serializers.branch_account_serializer import BranchAccountSerializer
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
<<<<<<< HEAD
from config.utilities.pagination import StandardResultsSetPagination
from config.utilities.get_queryset import get_account_company_queryset
=======
from config.pagination.pagination import StandardResultsSetPagination
from config.utilities.get_queryset import get_company_queryset
>>>>>>> 953fc17 (accounts)
from accounts.permissions.account_permissions import AccountPermission
from accounts.services.accounts_service import AccountsService
from company.models.company_model import Company
from django.core.exceptions import ObjectDoesNotExist
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
        try:
            """Return BranchAccount queryset filtered by the logged-in company/user."""
            return get_account_company_queryset(self.request, BranchAccount).select_related('branch', 'account')
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {e}"

    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        branch_account = serializer.save(company=company) #Add branch = self.request.user.branch
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(branch=branch_account.branch.name, account_number=branch_account.account.account_number).success(
            f"BranchAccount for branch '{branch_account.branch.name}' and account '{branch_account.account.name}' (Number: {branch_account.account.account_number}) created by {actor} in company '{getattr(company, 'name', 'Unknown')}'."
        )
    
    def perform_update(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        branch_account = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(branch=branch_account.branch.name, account_number=branch_account.account.account_number).info(
            f"BranchAccount for branch '{branch_account.branch.name}' and account '{branch_account.account.name}' (Number: {branch_account.account.account_number}) updated by {actor}."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(branch=instance.branch.name, account_number=instance.account.account_number).warning(
            f"BranchAccount for branch '{instance.branch.name}' and account '{instance.account.name}' (Number: {instance.account.account_number}) deleted by {actor}."
        )
        instance.delete()


class GetBranchAccountTransactions(APIView):
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
        
         # Check permissions
        if not AccountPermission().has_object_permission(request, self, account):
            logger.warning(f"Unauthorized access attempt to Account ID {account_id} by user {request.user}.")
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        # Ensure the user belongs to a branch
        user_branch = getattr(request.user, "branch", None)
        if user_branch is None:
            logger.warning(f"User {request.user} has no branch associated.")
            return Response({"detail": "User has no branch assigned."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate BranchAccount existence
        branch_account = account.branch_accounts.filter(branch=user_branch).first()
        if not branch_account:
            logger.warning(f"BranchAccount not found for Account {account_id} and Branch {user_branch.id}.")
            return Response({"detail": "BranchAccount not found."}, status=status.HTTP_404_NOT_FOUND)

        # Fetch transactions
        transactions = AccountsService.get_account_transactions(account)
        branch_transactions = transactions.filter(branch_id=user_branch)
        serializer = TransactionSerializer(branch_transactions, many=True)

        logger.info(
            f"Retrieved {len(branch_transactions)} transactions "
            f"for Account ID {account_id} by user {request.user}."
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    


class GetBranchAccountBalance(APIView):
    """
    API View to retrieve the balance of a specific branch account.
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
        
        # validate user belongs to a branch
        user_branch = getattr(request.user, "branch", None)
        if user_branch is None:
            logger.warning(f"User {request.user} has no branch associated.")
            return Response({"detail": "User must be linked to a branch."}, status=status.HTTP_403_FORBIDDEN)
        branch_account = account.branch_accounts.filter(branch=user_branch).first()
        if not branch_account:
            logger.warning(f"BranchAccount not found for Account {account_id} and Branch {user_branch.id}.")
            return Response({"detail": "BranchAccount not found."}, status=status.HTTP_404_NOT_FOUND)

        balance = branch_account.account.balance
        logger.info(f"Retrieved balance for Account ID {account_id} by user {request.user}: {balance}")
        return Response({"account_id": account_id, "balance": balance}, status=status.HTTP_200_OK)
    


class FreezeBranchAccount(APIView):
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


        user_branch = getattr(request.user, "branch", None)
        if user_branch is None:
            logger.warning(f"User {request.user} has no branch associated.")
            return Response({"detail": "User has no branch assigned."}, status=status.HTTP_400_BAD_REQUEST)
        
        
        branch_account = account.branch_accounts.filter(branch=user_branch).first()
        if not branch_account:
            logger.warning(f"BranchAccount not found for Account {account_id} and Branch {user_branch.id}.")
            return Response({"detail": "BranchAccount not found."}, status=status.HTTP_404_NOT_FOUND)
        
        branch_account.account.is_frozen = True
        try:
            branch_account.account.save(update_fields=['is_frozen'])
        except Exception as e:
            logger.error(f"Failed to freeze Account {account_id}: {e}")
            return Response({"detail": f"Failed to freeze account {account_id}."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.info(f"Account ID {account_id} frozen by user {request.user}.")
        return Response({"detail": f"Account {account_id} has been frozen."}, status=status.HTTP_200_OK)
    


class UnfreezeBranchAccount(APIView):
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
        
        user_branch = getattr(request.user, "branch", None)
        if user_branch is None:
            logger.warning(f"User {request.user} has no branch associated.")
            return Response({"detail": "User has no branch assigned."}, status=status.HTTP_400_BAD_REQUEST)
        
        branch_account = account.branch_accounts.filter(branch=user_branch).first()
        if not branch_account:
            logger.warning(f"BranchAccount not found for Account {account_id} and Branch {user_branch.id}.")
            return Response({"detail": "BranchAccount not found."}, status=status.HTTP_404_NOT_FOUND)
        try:
            AccountsService.unfreeze_account(branch_account.account)
        except Exception as e:
            logger.error(f"Failed to unfreeze Account {account_id}: {e}")
            return Response({"detail": f"Failed to unfreeze account {account_id}."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.info(f"Account ID {account_id} unfrozen by user {request.user}.")
        return Response(
            {"detail": f"Account {account_id} has been unfrozen.", "is_frozen": False}, 
            status=status.HTTP_200_OK
        )

        