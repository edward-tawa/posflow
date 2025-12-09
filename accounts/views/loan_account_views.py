from rest_framework.viewsets import ModelViewSet
from accounts.models.loan_account_model import LoanAccount
from accounts.models.supplier_account import SupplierAccount
from loans.permissions.loan_permissions import LoanPermissions
from accounts.serializers.loan_account_serializer import LoanAccountSerializer
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
from config.utilities.pagination import StandardResultsSetPagination
from config.utilities.get_queryset import get_account_company_queryset
from accounts.permissions.account_permissions import AccountPermission
from suppliers.permissions.supplier_permissions import SupplierPermissions
from accounts.services.accounts_service import AccountsService
from company.models.company_model import Company
from django.core.exceptions import ObjectDoesNotExist
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
        try:
            """Return LoanAccount queryset filtered by the logged-in company/user."""
            return get_account_company_queryset(self.request, LoanAccount).select_related('loan', 'account')
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {e}"

    def perform_create(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        loan_account = serializer.save(company=company)#Replace company with branch
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(loan=loan_account.loan.borrower.first_name, account_number=loan_account.account.account_number).success(
            f"LoanAccount for loan '{loan_account.loan.borrower.first_name}' and account '{loan_account.account.name}' (Number: {loan_account.account.account_number}) created by {actor} in company '{getattr(company, 'name', 'Unknown')}'."
        )
    
    def perform_update(self, serializer):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        loan_account = serializer.save()
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(loan=loan_account.loan.borrower.username, account_number=loan_account.account.account_number).info(
            f"LoanAccount for loan '{loan_account.loan.borrower.username}' and account '{loan_account.account.name}' (Number: {loan_account.account.account_number}) updated by {actor}."
        )

    def perform_destroy(self, instance):
        user = self.request.user
        company = getattr(user, 'company', None) or (user if isinstance(user, Company) else None)
        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
        logger.bind(loan=instance.loan.borrower.username, account_number=instance.account.account_number).warning(
            f"LoanAccount for loan '{instance.loan.borrower.username}' and account '{instance.account.name}' (Number: {instance.account.account_number}) deleted by {actor}."
        )
        instance.delete()




class GetLoanAccountTransactions(APIView):
    """
    API View to retrieve transactions for a specific loan account.
    """
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [AccountPermission, IsAuthenticated]

    def get(self, request, loan_account_id):
        try:
            loan_account = LoanAccount.objects.get(id=loan_account_id)
        except LoanAccount.DoesNotExist:
            logger.warning(f"LoanAccount with ID {loan_account_id} does not exist.")
            return Response({"detail": "LoanAccount not found."}, status=status.HTTP_404_NOT_FOUND)
        
         # Check permissions
        if not AccountPermission().has_object_permission(request, self, loan_account):
            logger.warning(f"Unauthorized access attempt to Account ID {loan_account_id} by user {request.user.username}.")
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        # Ensure the user belongs to a branch
        user_branch = getattr(request.user, "branch", None)
        if user_branch is None:
            logger.warning(f"User {request.user.username} has no branch associated.")
            return Response({"detail": "User has no branch assigned."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch transactions
        loan_account_transactions = Transaction.objects.filter(
                                    account=loan_account,
                                    company=request.user.company,
                                    branch=user_branch
                                )
        serializer = TransactionSerializer(loan_account_transactions, many=True)

        logger.info(
            f"Retrieved {len(loan_account_transactions)} transactions "
            f"for Account ID {loan_account_id} by user {request.user.username}."
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    


class GetLoanAccountBalance(APIView):
    """
    API View to retrieve the balance of a specific loan account.
    """
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [AccountPermission, IsAuthenticated]

    def get(self, request, loan_account_id):
        try:
            loan_account = LoanAccount.objects.get(id=loan_account_id)
        except LoanAccount.DoesNotExist:
            logger.warning(f"LoanAccount with ID {loan_account_id} does not exist.")
            return Response({"detail": "LoanAccount not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if not AccountPermission().has_object_permission(request, self, loan_account):
            logger.warning(f"Unauthorized access attempt to Account ID {loan_account_id} by user {request.user.username}.")
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        # validate user belongs to a branch
        user_branch = getattr(request.user, "branch", None)
        if user_branch is None:
            logger.warning(f"User {request.user} has no branch associated.")
            return Response({"detail": "User must be linked to a branch."}, status=status.HTTP_403_FORBIDDEN)
        loan_account = LoanAccount.objects.filter(
                                id=loan_account_id,
                                branch=user_branch,
                                company=request.user.company
                            ).first()
        if not loan_account:
            logger.warning(f"LoanAccount not found for LoanAccount {loan_account_id}.")
            return Response({"detail": "LoanAccount not found."}, status=status.HTTP_404_NOT_FOUND)

        balance = loan_account.account.balance
        logger.info(f"Retrieved balance for Account ID {loan_account.id} by user {request.user.username}: {balance}")
        return Response({"account_id": loan_account.id, "balance": balance}, status=status.HTTP_200_OK)
    


class FreezeLoanAccount(APIView):
    """
    API View to freeze a specific loan account.
    """
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [AccountPermission, IsAuthenticated]

    def post(self, request, loan_account_id):
        try:
            loan_account = LoanAccount.objects.get(id=loan_account_id)
        except LoanAccount.DoesNotExist:
            logger.warning(f"LoanAccount with ID {loan_account_id} does not exist.")
            return Response({"detail": "LoanAccount not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if not AccountPermission().has_object_permission(request, self, loan_account):
            logger.warning(f"Unauthorized freeze attempt on LoanAccount ID {loan_account_id} by user {request.user}.")
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)


        user_branch = getattr(request.user, "branch", None)
        if user_branch is None:
            logger.warning(f"User {request.user.username} has no branch associated.")
            return Response({"detail": "User has no branch assigned."}, status=status.HTTP_403_FORBIDDEN)
        
        
        loan_account = LoanAccount.objects.filter(id=loan_account_id,
                                                           branch=user_branch, company=request.user.company).first()
        if not loan_account:
            logger.warning(f"LoanAccount not found for LoanAccount {loan_account_id} and Branch {user_branch.id}.")
            return Response({"detail": "LoanAccount not found."}, status=status.HTTP_404_NOT_FOUND)
        
        loan_account.account.is_frozen = True
        try:
            loan_account.account.save(update_fields=['is_frozen'])
        except Exception as e:
            logger.error(f"Failed to freeze Account {loan_account_id}: {e}")
            return Response({"detail": f"Failed to freeze account {loan_account_id}."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logger.info(f"LoanAccount ID {loan_account_id} frozen by user {request.user.username}.")
        return Response({"detail": f"LoanAccount {loan_account_id} has been frozen."}, status=status.HTTP_200_OK)
    


class UnfreezeLoanAccount(APIView):
    """
    API View to unfreeze a specific loan account.
    """
    authentication_classes = [UserCookieJWTAuthentication, CompanyCookieJWTAuthentication, JWTAuthentication]
    permission_classes = [AccountPermission, IsAuthenticated]

    def post(self, request, loan_account_id):
        try:
            loan_account = LoanAccount.objects.get(id=loan_account_id)
        except LoanAccount.DoesNotExist:
            logger.warning(f"LoanAccount with ID {loan_account_id} does not exist.")
            return Response({"detail": "LoanAccount not found."}, status=status.HTTP_404_NOT_FOUND)

        if not AccountPermission().has_object_permission(request, self, loan_account):
            logger.warning(f"Unauthorized unfreeze attempt on LoanAccount ID {loan_account_id} by user {request.user.username}.")
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        user_branch = getattr(request.user, "branch", None)
        if user_branch is None:
            logger.warning(f"User {request.user.username} has no branch associated.")
            return Response({"detail": "User has no branch assigned."}, status=status.HTTP_403_FORBIDDEN)
        
        loan_account = LoanAccount.objects.filter(id=loan_account_id, branch=user_branch, company=request.user.company).first()
        if not loan_account:
            logger.warning(f"LoanAccount not found for loan {loan_account_id} and Branch {user_branch.id}.")
            return Response({"detail": "LoanAccount not found."}, status=status.HTTP_404_NOT_FOUND)
        try:
            AccountsService.unfreeze_account(loan_account.account)
        except Exception as e:
            logger.error(f"Failed to unfreeze Account {loan_account.account.id}: {e}")
            return Response({"detail": f"Failed to unfreeze account {loan_account.id} for loan account {loan_account_id}."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.info(f"Account ID {loan_account.id} unfrozen by user {request.user.username}.")
        return Response(
            {"detail": f"Account {loan_account.account.id} has been unfrozen.", "is_frozen": False}, 
            status=status.HTTP_200_OK
        )