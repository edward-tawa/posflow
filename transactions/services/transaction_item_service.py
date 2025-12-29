from transactions.models.transaction_item_model import TransactionItem
from transactions.services.transaction_service import TransactionService
from transactions.models.transaction_model import Transaction
from inventory.models.product_model import Product
from django.db import transaction
from django.db import QuerySet
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

        if transaction.transaction_type == Transaction.CASH_TRANSFER and product is not None:
            raise ValidationError("Cannot attach a product item to a cash transfer transaction.")

        item = TransactionItem.objects.create(
            transaction=transaction,
            product=product,
            product_name=product_name,
            quantity=quantity,
            unit_price=unit_price,
            tax_rate=tax_rate
        )
        logger.info(f"Transaction item created | id={item.id}")
        TransactionService.recalculate_totals(transaction)
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
        TransactionService.recalculate_totals(item.transaction)
        return item

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def delete_transaction_item(item: TransactionItem) -> None:
        transaction_ref = item.transaction
        item_id = item.id
        item.delete()
        logger.info(f"Transaction item deleted | id={item_id}")
        TransactionService.recalculate_totals(transaction_ref)

    # -------------------------
    # ATTACH / DETACH
    # -------------------------
    @staticmethod
    @transaction.atomic
    def attach_to_transaction(
        item: TransactionItem,
        transaction: Transaction
    ) -> TransactionItem:

        old_transaction = item.transaction

        if transaction.transaction_type == Transaction.CASH_TRANSFER and item.product is not None:
            raise ValidationError("Cannot attach a product item to a cash transfer transaction.")

        item.transaction = transaction
        item.save(update_fields=['transaction'])
        logger.info(f"Transaction item '{item.id}' attached to transaction '{transaction.id}'.")

        TransactionService.recalculate_totals(transaction)
        if old_transaction:
            TransactionService.recalculate_totals(old_transaction)
        return item

    @staticmethod
    @transaction.atomic
    def detach_from_transaction(item: TransactionItem) -> TransactionItem:
        # If transaction FK is non-nullable, raise an error instead of setting None
        raise ValidationError("Cannot detach item from transaction because transaction field is non-nullable.")
    
    # -------------------------
    # STATUS
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_transaction_item_status(
        item: TransactionItem,
        new_status: str
    ) -> TransactionItem:

        ALLOWED_STATUSES = {"pending", "completed", "canceled"}

        if new_status not in ALLOWED_STATUSES:
            logger.error(f"Attempted to set invalid status '{new_status}' for transaction item '{item.id}'.")
            raise ValueError(f"Invalid status: {new_status}")

        item.status = new_status
        item.save(update_fields=['status'])
        logger.info(f"Transaction item '{item.id}' status updated to '{new_status}'.")
        return item

    # -------------------------
    # GETTERS
    # -------------------------
    @staticmethod
    def get_transaction_item_by_id(item_id: int) -> TransactionItem:
        try:
            return TransactionItem.objects.get(id=item_id)
        except TransactionItem.DoesNotExist:
            logger.error(f"Transaction item with id '{item_id}' does not exist.")
            raise

    @staticmethod
    def get_transaction_items_by_transaction(transaction: Transaction) -> QuerySet[TransactionItem]:
        return TransactionItem.objects.filter(transaction=transaction).order_by('created_at')

    @staticmethod
    def list_all_transaction_items() -> QuerySet[TransactionItem]:
        return TransactionItem.objects.all().order_by('created_at')

    @staticmethod
    def list_transaction_items_by_status(status: str) -> QuerySet[TransactionItem]:
        return TransactionItem.objects.filter(status=status).order_by('created_at')

    @staticmethod
    def count_transaction_items() -> int:
        return TransactionItem.objects.count()
