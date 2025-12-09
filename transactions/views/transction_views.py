from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.utilities.pagination import StandardResultsSetPagination
from transactions.permissions.transaction_permissions import TransactionPermissions
from transactions.models import Transaction
from transactions.serializers.transaction_serializer import TransactionSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from transactions.services.transcation_service import TransactionService
from loguru import logger


class TransactionViewSet(ModelViewSet):
    """
    ViewSet for managing Transactions.
    Supports listing, retrieving, creating, updating, and deleting transactions.
    Includes filtering, searching, ordering, and detailed logging.
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = [TransactionPermissions]  # Add your custom permissions

    # Filtering, search & ordering
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'transaction_number',
        'transaction_type',
        'company__name',
        'branch__name'
    ]
    ordering_fields = ['created_at', 'updated_at', 'transaction_date', 'total_amount']
    ordering = ['-created_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            """
            Returns the Transaction queryset filtered by the logged-in company/user.
            """
            return (
                get_company_queryset(self.request, Transaction)
                .select_related('company', 'branch')
            )
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {e}"

    def perform_create(self, serializer):
        """
        Saves a new Transaction instance and logs the event.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        transaction = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.success(
            f"Transaction '{transaction.transaction_number}' created by '{actor}' "
            f"for company '{transaction.company.name}'."
        )

    def perform_update(self, serializer):
        """
        Saves an updated Transaction instance and logs the event.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        transaction = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"Transaction '{transaction.transaction_number}' updated by '{actor}' "
            f"for company '{transaction.company.name}'."
        )

    def perform_destroy(self, instance):
        """
        Deletes a Transaction instance and logs the event.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        transaction_number = instance.transaction_number
        instance.delete()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.warning(
            f"Transaction '{transaction_number}' deleted by '{actor}' "
            f"from company '{company.name}'."
        )



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
            actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')
            logger.info(f'Transaction {transaction.transaction_number} reversed by {actor} for company {company.name}')
            return Response({"status":"Success", "message":f"Transaction '{transaction.transaction_number}' reversed successfully."}, status=status.HTTP_200_OK)
        
        except Transaction.DoesNotExist:
            logger.info(f"Transaction with id {transaction_id} does not exist")
            return Response({"status":"Failure", "message":"Transaction not found."}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            logger.exception(f"Error reversing transaction {transaction_id}")
            return Response({"status":"Failure", "message":"An error occurred while reversing the transaction."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





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


