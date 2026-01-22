from decimal import Decimal
from transactions.models.transaction_item_model import TransactionItem
from transactions.services.transaction_item_service import TransactionItemService
from transactions.models.transaction_model import Transaction


def create_transaction_items_util(
        transaction: Transaction,
        items: list[dict]
) -> list[TransactionItem]:
    """
    Utility function to create multiple transaction items.
    """
    created_items = []
    for item_data in items:
        item = TransactionItemService.create_transaction_item(
            transaction=transaction,
            product=item_data.get('product'),
            product_name=item_data.get('product_name'),
            quantity=item_data.get('quantity', 1),
            unit_price=item_data.get('unit_price', Decimal('0.00')),
            tax_rate=item_data.get('tax_rate', Decimal('0.00'))
        )
        created_items.append(item)

    return created_items