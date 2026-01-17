from transactions.models.transaction_item_model import TransactionItem
from transactions.services.transaction_service import TransactionService
from transactions.models.transaction_model import Transaction
from inventory.models.product_model import Product
from django.db import transaction
from django.db import QuerySet
from django.core.exceptions import ValidationError
from loguru import logger
from decimal import Decimal



class TransactionItemQueryService:
    """
    Handles queries, listing, and counting of TransactionItems.
    """

    @staticmethod
    def get_transaction_item_by_id(item_id: int) -> TransactionItem:
        """
        Docstring for get_transaction_item_by_id
        Retrieve a TransactionItem by its unique ID.
        """
        try:
            return TransactionItem.objects.get(id=item_id)
        except TransactionItem.DoesNotExist:
            logger.error(f"Transaction item with id '{item_id}' does not exist.")
            raise

    @staticmethod
    def get_transaction_items_by_transaction(transaction: Transaction) -> QuerySet[TransactionItem]:
        """
        Docstring for get_transaction_items_by_transaction
        
        Retrieve all TransactionItems associated with a specific Transaction.
        """
        return TransactionItem.objects.filter(transaction=transaction).order_by('created_at')

    @staticmethod
    def list_all_transaction_items() -> QuerySet[TransactionItem]:
        """
        Docstring for list_all_transaction_items
        
        Retrieve all TransactionItems in the system.
        """
        return TransactionItem.objects.all().order_by('created_at')

    @staticmethod
    def list_transaction_items_by_status(status: str) -> QuerySet[TransactionItem]:
        """
        Docstring for list_transaction_items_by_status
        
        Retrieve TransactionItems filtered by their status.
        """
        return TransactionItem.objects.filter(status=status).order_by('created_at')

    @staticmethod
    def count_transaction_items() -> int:
        """
        Docstring for count_transaction_items
        
        Count the total number of TransactionItems in the system.
        """
        return TransactionItem.objects.count()
