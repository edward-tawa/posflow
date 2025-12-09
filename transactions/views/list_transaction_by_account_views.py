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


class ListTransactionsByAccount(APIView):
    permission_classes = [TransactionPermissions]
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]

    def get(self, request, account_id):
        """
        Lists all transactions for a specific account.
        """
        company = get_logged_in_company(request)
        user = request.user
        branch = user.branch
        try:
            account = Account.objects.get(id=account_id, branch=branch, company=company)
            transactions = TransactionService.list_transactions_by_account(account)
            serializer = TransactionSerializer(transactions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        

        except Account.DoesNotExist:
            logger.exception(f"Account with id {account_id} was not found")
            return Response({"status":"Failure", "message":"Account not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(f"Error listing transactions for account {account_id}")
            return Response({"status":"Failure", "message":"An error occurred while retrieving transactions."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)