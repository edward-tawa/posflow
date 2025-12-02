from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.auth.jwt_token_authentication import CompanyCookieJWTAuthentication, UserCookieJWTAuthentication
from config.utilities.get_queryset import get_company_queryset
from config.utilities.get_logged_in_company import get_logged_in_company
from config.utilities.pagination import StandardResultsSetPagination
from transactions.models import TransactionItem
from transactions.serializers.transaction_item_serializer import TransactionItemSerializer
from loguru import logger


class TransactionItemViewSet(ModelViewSet):
    """
    ViewSet for managing Transaction Items.
    Supports listing, retrieving, creating, updating, and deleting transaction items.
    Includes filtering, search, ordering, company scoping, and detailed logging.
    """
    queryset = TransactionItem.objects.all()
    serializer_class = TransactionItemSerializer
    authentication_classes = [
        CompanyCookieJWTAuthentication,
        UserCookieJWTAuthentication,
        JWTAuthentication
    ]
    permission_classes = []  # Add custom permissions when needed

    filter_backends = [SearchFilter, OrderingFilter]

    # searching inside relations
    search_fields = [
        'transaction__transaction_number',
        'product__name',
    ]

    ordering_fields = [
        'created_at',
        'updated_at',
        'quantity',
        'unit_price',
        # 'total_price',
    ]
    ordering = ['-created_at']

    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        Returns TransactionItem queryset filtered by logged-in company.
        """
        return (
            get_company_queryset(self.request, TransactionItem)
            .select_related('transaction', 'product', 'transaction__company')
        )

    def perform_create(self, serializer):
        """
        Create a TransactionItem with logging.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"TransactionItem '{item.id}' created for transaction "
            f"'{item.transaction.transaction_number}' by '{actor}'."
        )

    def perform_update(self, serializer):
        """
        Update a TransactionItem with logging.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        item = serializer.save()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.info(
            f"TransactionItem '{item.id}' updated for transaction "
            f"'{item.transaction.transaction_number}' by '{actor}'."
        )

    def perform_destroy(self, instance):
        """
        Delete a TransactionItem with logging and update transaction total.
        """
        user = self.request.user
        company = get_logged_in_company(self.request)

        transaction = instance.transaction
        item_id = instance.id

        instance.delete()

        # Update transaction total after delete
        transaction.update_total_amount()

        actor = getattr(company, 'name', None) or getattr(user, 'username', 'Unknown')

        logger.warning(
            f"TransactionItem '{item_id}' deleted from transaction "
            f"'{transaction.transaction_number}' by '{actor}'."
        )
