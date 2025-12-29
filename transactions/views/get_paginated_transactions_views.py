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




class GetPaginatedTransactionsView(APIView):
    permission_classes = [TransactionPermissions]
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    pagination_class = StandardResultsSetPagination

    def get(self, request, account_id):
        company = get_logged_in_company(request)

        try:
            account = Account.objects.get(id=account_id, company=company)
            qs = TransactionService.get_transactions(account=account, company=company)

            # DRF pagination
            paginator = self.pagination_class()
            paginated_qs = paginator.paginate_queryset(qs, request)
            serializer = TransactionSerializer(paginated_qs, many=True)
            return paginator.get_paginated_response(serializer.data)

        except Account.DoesNotExist:
            return Response(
                {"status": "Failure", "message": "Account not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception("Error retrieving transactions")
            return Response(
                {"status": "Failure", "message": "An error occurred while retrieving transactions."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
