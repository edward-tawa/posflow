from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.pagination.pagination import StandardResultsSetPagination
from transactions.permissions.transaction_permissions import TransactionPermissions
from transactions.models import Transaction
from transactions.serializers.transaction_serializer import TransactionSerializer
from accounts.models.account_model import Account
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from transactions.services.transaction_service import TransactionService
from loguru import logger



class TransferFundsView(APIView):
    permission_classes = [TransactionPermissions]
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]

    def post(self, request):
        """
        Transfers funds between accounts and logs the event.
        Expects 'from_account_id', 'to_account_id', and 'amount' in the request data.
        """
        company = get_logged_in_company(request)
        user = request.user
        branch = user.branch

        from_account_id = request.data.get('from_account_id')
        to_account_id = request.data.get('to_account_id')
        amount = request.data.get('amount')

        try:
            transaction = TransactionService.transfer_funds(
                from_account_id, to_account_id, amount)
            actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
            logger.info(f'Funds transferred by {actor} for company {company.name}')
            return Response({"status":"Success", "message":f"Funds transferred successfully in transaction '{transaction.transaction_number}'."}, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.exception("Error transferring funds")
            return Response({"status":"Failure", "message":"An error occurred while transferring funds."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




