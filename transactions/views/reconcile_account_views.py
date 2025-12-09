from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from accounts.serializers.account_serializer import AccountSerializer
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




class ReconcileTransactionView(APIView):
    """
    APIView for reconciling Transactions.
    Supports pagination and detailed logging.
    """
    serializer_class = AccountSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]

    def get(self, request, account_id):
        """
        GET()
        -------------------
        Retrieves Reconciled Transactions
        -------------------
        """
        user = request.user
        company = get_logged_in_company(request)
        branch = getattr(user, 'branch', None)

        try:
            account = Account.objects.get(id=account_id, company=company, branch=branch)
            TransactionService.reconcile_transactions(account)
        except Account.DoesNotExist:
            logger.error(f"Account with id '{account_id}' does not exist.")
            return Response(
                {"detail": "Account not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error reconciling transactions for account '{account_id}': {str(e)}")
            return Response(
                {"detail": "Error reconciling transactions."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        logger.info(f"Reconciled transactions for account '{account.name}'")
        return Response(
            {"account_id": account_id, "detail": "Transactions reconciled successfully."},
            status=status.HTTP_200_OK
        )