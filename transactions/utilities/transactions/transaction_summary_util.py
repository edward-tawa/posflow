from transactions.services.transaction_service import TransactionService
from transactions.models.transaction_model import Transaction

def get_transaction_summary_util(
        transaction: Transaction,
) -> dict:
    """
    Utility function to get a summary of a transaction.
    """
    summary = TransactionService.get_transaction_summary(
        transaction=transaction
    )
    return summary