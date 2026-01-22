from transactions.services.transaction_service import TransactionService
from transactions.models.transaction_model import Transaction



def create_transaction_util(
        company,
        branch,
        debit_account,
        credit_account,
        transaction_type,
        transaction_category,
        total_amount,
        customer=None,
        supplier=None,
        product=None
) -> Transaction:
    """
    Utility function to create a transaction.
    """
    transaction = TransactionService.create_transaction(
        company=company,
        branch=branch,
        debit_account=debit_account,
        credit_account=credit_account,
        transaction_type=transaction_type,
        transaction_category=transaction_category,
        total_amount=total_amount,
        customer=customer,
        supplier=supplier,
        product=product
    )
    return transaction