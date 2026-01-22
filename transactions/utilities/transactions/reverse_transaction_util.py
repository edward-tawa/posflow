from transactions.services.transaction_service import TransactionService
from transactions.models.transaction_model import Transaction



def reverse_transaction_util(
        transaction: Transaction,
) -> Transaction:
    """
    Utility function to reverse a transaction.
    """
    reversed_transaction = TransactionService.reverse_transaction(
        transaction=transaction
    )
    return reversed_transaction