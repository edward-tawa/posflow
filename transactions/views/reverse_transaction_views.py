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



class ReverseTransactionView(APIView):
    permission_classes = [TransactionPermissions]
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]

    def post(self, request, transaction_id):
        """
        Reverses a transaction by its ID and logs the event.
        """
        company = get_logged_in_company(request)
        user = request.user
        branch = user.branch
        try:
            transaction = Transaction.objects.get(id=transaction_id, branch=branch, company=company)
            TransactionService.reverse_transaction(transaction)
            transaction.reversal_applied = True  # Mark reversal as applied
            transaction.save(update_fields=['reversal_applied']) # Save the change
            actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
            logger.info(f'Transaction {transaction.transaction_number} reversed by {actor} for company {company.name}')
            return Response({"status":"Success", "message":f"Transaction '{transaction.transaction_number}' reversed successfully."}, status=status.HTTP_200_OK)
        
        except Transaction.DoesNotExist:
            logger.info(f"Transaction with id {transaction_id} does not exist")
            return Response({"status":"Failure", "message":"Transaction not found."}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logger.exception(f"Error reversing transaction {transaction_id}")
            return Response({"status":"Failure", "message":"An error occurred while reversing the transaction."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





