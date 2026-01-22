from transactions.services.transaction_service import TransactionService
from transactions.models.transaction_model import Transaction

def validate_transaction_util(
        transaction: Transaction,
):
    """
    Utility function to validate a transaction.
    """
    # Call the service method to validate the transaction
    TransactionService.validate_transaction(transaction)