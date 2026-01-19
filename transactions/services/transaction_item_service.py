from transactions.models.transaction_item_model import TransactionItem
# from transactions.services.transaction_service import TransactionService
from transactions.models.transaction_model import Transaction
from inventory.models.product_model import Product
from django.db import transaction
# from django.db import QuerySet
from django.core.exceptions import ValidationError
from loguru import logger
from decimal import Decimal


class TransactionItemService:
    """
    Service layer for Transaction Item domain operations.
    """

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def create_transaction_item(
        transaction: Transaction,
        product: Product = None,
        product_name: str = "",
        quantity: int = 1,
        unit_price: Decimal = Decimal("0.00"),
        tax_rate: Decimal = Decimal("0.00")
    ) -> TransactionItem:
        """Create a new Transaction Item and associate it with the given Transaction."""

        if transaction.transaction_type == Transaction.CASH_TRANSFER and product is not None:
            raise ValidationError("Cannot add a product item to a cash transfer transaction.")

        item = TransactionItem.objects.create(
            transaction=transaction,
            product=product,
            product_name=product_name,
            quantity=quantity,
            unit_price=unit_price,
            tax_rate=tax_rate
        )
        logger.info(f"Transaction item created | id={item.id}")
        TransactionItemService.add_to_transaction(item, transaction)
        transaction.update_total_amount()
        return item


    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_transaction_item(
        item: TransactionItem,
        product: Product = None,
        product_name: str = None,
        quantity: int = None,
        unit_price: Decimal = None,
        tax_rate: Decimal = None
    ) -> TransactionItem:
        """Update fields of the Transaction Item."""

        if product is not None:
            item.product = product
        if product_name is not None:
            item.product_name = product_name
        if quantity is not None:
            item.quantity = quantity
        if unit_price is not None:
            item.unit_price = unit_price
        if tax_rate is not None:
            item.tax_rate = tax_rate

        item.save()
        logger.info(f"Transaction item updated | id={item.id}")
        item.transaction.update_total_amount()
        return item


    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def delete_transaction_item(item: TransactionItem) -> None:
        """Delete the specified Transaction Item."""
        transaction_ref = item.transaction
        item_id = item.id
        item.delete()
        logger.info(f"Transaction item deleted | id={item_id}")
        transaction_ref.update_total_amount()


    # -------------------------
    # ATTACH / DETACH
    # -------------------------
    @staticmethod
    @transaction.atomic
    def add_to_transaction(
        item: TransactionItem,
        transaction: Transaction
    ) -> TransactionItem:
        """Adds the TransactionItem to the specified Transaction."""

        old_transaction = item.transaction

        if transaction.transaction_type not in [t[0] for t in Transaction.TRANSACTION_TYPE] and item.product is not None:
            raise ValidationError("Cannot add a product item to a cash transfer or credit transaction.")

        item.transaction = transaction
        item.save(update_fields=['transaction'])
        logger.info(f"Transaction item '{item.id}' added to transaction '{transaction.id}'.")

        transaction.update_total_amount()
        if old_transaction:
            old_transaction.update_total_amount()
        return item


    @staticmethod
    @transaction.atomic
    def remove_from_transaction(item: TransactionItem) -> TransactionItem:
        # If transaction FK is non-nullable, raise an error instead of setting None
        raise ValidationError("Cannot remove item from transaction because transaction field is non-nullable.")
    

    # -------------------------
    # STATUS
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_transaction_item_status(
        item: TransactionItem,
        new_status: str
    ) -> TransactionItem:
        """Update the status of the Transaction Item."""

        ALLOWED_STATUSES = {"pending", "completed", "canceled"}

        if new_status not in ALLOWED_STATUSES:
            logger.error(f"Attempted to set invalid status '{new_status}' for transaction item '{item.id}'.")
            raise ValueError(f"Invalid status: {new_status}")

        item.status = new_status
        item.save(update_fields=['status'])
        logger.info(f"Transaction item '{item.id}' status updated to '{new_status}'.")
        return item

    