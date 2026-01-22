from transactions.services.transaction_item_service import TransactionItemService
from transactions.models.transaction_item_model import TransactionItem
from transactions.models.transaction_model import Transaction



def add_transaction_item_to_transaction_util(
        item: TransactionItem,
        transaction: Transaction,
) -> None:
    """
    Utility function to add a transaction item to a transaction.
    """
    TransactionItemService.add_to_transaction(
        transaction_item = item,
        transaction=transaction,
    )