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



class GetTransactionsByDateRangeView(APIView):
    permission_classes = [TransactionPermissions]
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]

    def get(self, request):
        """
        Retrieves transactions within a specified date range.
        Expects 'start_date' and 'end_date' as query parameters in 'YYYY-MM-DD' format.
        """
        company = get_logged_in_company(request)
        user = request.user
        branch = user.branch

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        try:
            transactions = TransactionService.get_transactions_by_date_range(start_date, end_date)
            serializer = TransactionSerializer(transactions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception("Error retrieving transactions by date range")
            return Response({"status":"Failure", "message":"An error occurred while retrieving transactions."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

