from decimal import Decimal
from transactions.models.transaction_item_model import TransactionItem
from transactions.services.transaction_item_service import TransactionItemService
from transactions.models.transaction_model import Transaction


def create_transaction_item_util(
        transaction: Transaction,
        product,
        product_name: str,
        quantity: int = 1,
        unit_price: Decimal = 0.0,
        tax_rate: Decimal = 0.0
) -> TransactionItem:
    """
    Utility function to create a transaction item.
    """
    item = TransactionItemService.create_transaction_item(
        transaction=transaction,
        product=product,
        product_name=product_name,
        quantity=quantity,
        unit_price=unit_price,
        tax_rate=tax_rate
    )

    return item