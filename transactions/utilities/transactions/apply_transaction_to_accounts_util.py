from decimal import Decimal
from transactions.models.transaction_item_model import TransactionItem
from transactions.services.transaction_service import TransactionService
from transactions.models.transaction_model import Transaction


def apply_transaction_to_accounts_util(
        transaction: Transaction,
):
    """
    Utility function to apply a transaction to accounts.
    """
    # Call the service method to apply the transaction to accounts
    TransactionService.apply_transaction_to_accounts(transaction)