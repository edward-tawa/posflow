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




class SearchTransactionView(APIView):
    """
    APIView for searching Transactions.
    Supports searching by reference number, account name, and description.
    Includes pagination and detailed logging.
    """
    serializer_class = TransactionSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    pagination_class = StandardResultsSetPagination
    serializer_class = TransactionSerializer

    def get(self, request):
        """
        GET()
        -------------------
        Searches for Transactions based on query parameters.
        -------------------
        """
        query = request.query_params.get('query', '')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))

        transactions = TransactionService.search_transactions(query)
        paginator = StandardResultsSetPagination()
        paginator.page_size = page_size
        paginated_transactions = paginator.paginate_queryset(transactions, request)

        serializer = TransactionSerializer(paginated_transactions, many=True)
        logger.info(f"Search for Transactions with query '{query}' returned {len(paginated_transactions)} results on page {page}.")
        return paginator.get_paginated_response(serializer.data)
    
    