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
from transactions.services.transaction_service import TransactionService
from loguru import logger



class GetTransactionSummaryView(APIView):
    """
    APIView for retrieving Transaction Summaries.
    Supports pagination and detailed logging.
    """
    serializer_class = TransactionSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]

    def get(self, request, transaction_id):
        """
        GET()
        -------------------
        Retrieves Transaction Summary for a specific transaction.
        -------------------
        """
        user = request.user
        company = get_logged_in_company(request)
        branch = getattr(user, 'branch', None)
        
        try:
            transaction = Transaction.objects.get(id=transaction_id, company=company, branch=branch)
            summary = TransactionService.get_transaction_summary(transaction)
        except Transaction.DoesNotExist:
            logger.error(f"Transaction with id '{transaction_id}' does not exist.")
            return Response(
                {"detail": "Transaction not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error retrieving transaction summary for transaction '{transaction_id}': {str(e)}")
            return Response(
                {"detail": "Error retrieving transaction summary."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        logger.info(f"Retrieved transaction summary for transaction '{transaction.id}': {summary}")
        return Response(
            {"transaction_id": transaction_id, "summary": summary},
            status=status.HTTP_200_OK
        )
        