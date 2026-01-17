from suppliers.models.purchase_return_item_model import PurchaseReturnItem
from suppliers.models.purchase_return_model import PurchaseReturn
from suppliers.models.supplier_model import Supplier
from loguru import logger
from django.db import transaction as db_transaction


class PurchaseReturnItemService:
    """
    Service class for managing purchase return items.
    Provides methods for creating, updating, deleting items,
    and attaching/detaching them to/from purchase returns.
    Includes logging and business rule enforcement.
    """

    ALLOWED_STATUSES = {"DRAFT", "APPROVED", "CANCELLED"}

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def create_item(
        purchase_return: PurchaseReturn,
        product,
        quantity: int,
        unit_price: float,
        tax_rate: float = 0,
        notes: str = ""
    ) -> PurchaseReturnItem:
        if quantity < 0 or unit_price < 0:
            raise ValueError("Quantity and unit price must be non-negative")

        item = PurchaseReturnItem.objects.create(
            purchase_return=purchase_return,
            product=product,
            quantity=quantity,
            unit_price=unit_price,
            tax_rate=tax_rate,
            # If you have a `notes` field on the model
            # notes=notes
        )

        logger.info(
            f"Purchase Return Item '{item.product.name}' created for return "
            f"'{item.purchase_return.id if item.purchase_return else 'None'}'."
        )
        return item

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_item(
        item: PurchaseReturnItem,
        product=None,
        quantity: int = None,
        unit_price: float = None,
        tax_rate: float = None,
        notes: str = None
    ) -> PurchaseReturnItem:

        updated = False

        if product is not None and item.product != product:
            item.product = product
            updated = True
        if quantity is not None:
            if quantity < 0:
                raise ValueError("Quantity must be non-negative")
            if item.quantity != quantity:
                item.quantity = quantity
                updated = True
        if unit_price is not None:
            if unit_price < 0:
                raise ValueError("Unit price must be non-negative")
            if item.unit_price != unit_price:
                item.unit_price = unit_price
                updated = True
        if tax_rate is not None and item.tax_rate != tax_rate:
            item.tax_rate = tax_rate
            updated = True
        # if notes field exists:
        # if notes is not None and item.notes != notes:
        #     item.notes = notes
        #     updated = True

        if updated:
            # Recalculate total_price if quantity, unit_price, or tax_rate changed
            item.save()
            logger.info(
                f"Purchase Return Item '{item.product.name}' updated in return "
                f"'{item.purchase_return.id if item.purchase_return else 'None'}'."
            )
        else:
            logger.info(
                f"No changes applied to Purchase Return Item '{item.product.name}' "
                f"in return '{item.purchase_return.id if item.purchase_return else 'None'}'."
            )

        return item

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_item(item: PurchaseReturnItem) -> None:
        return_id = item.purchase_return.id if item.purchase_return else 'None'
        item_name = item.product.name
        item.delete()
        logger.info(f"Deleted Purchase Return Item '{item_name}' from return '{return_id}'.")

    # -------------------------
    # RELATION MANAGEMENT
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def add_to_return(item: PurchaseReturnItem, purchase_return: PurchaseReturn) -> PurchaseReturnItem:
        previous_return = item.purchase_return
        item.purchase_return = purchase_return
        item.save(update_fields=['purchase_return'])

        if previous_return and previous_return != purchase_return:
            previous_return.update_total_amount()
        purchase_return.update_total_amount()

        logger.info(
            f"Purchase Return Item '{item.product.name}' attached to return '{purchase_return.id}' "
            f"(previous return: '{previous_return.id if previous_return else 'None'}')."
        )
        return item

    @staticmethod
    @db_transaction.atomic
    def remove_from_return(item: PurchaseReturnItem) -> PurchaseReturnItem:
        previous_return = item.purchase_return
        item.purchase_return = None
        item.save(update_fields=['purchase_return'])

        if previous_return:
            previous_return.update_total_amount()

        logger.info(
            f"Purchase Return Item '{item.product.name}' detached from return "
            f"'{previous_return.id if previous_return else 'None'}'."
        )
        return item

    # -------------------------
    # STATUS MANAGEMENT
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_item_status(item: PurchaseReturnItem, new_status: str) -> PurchaseReturnItem:
        if new_status not in PurchaseReturnItemService.ALLOWED_STATUSES:
            logger.error(
                f"Attempted to set invalid status '{new_status}' for item '{item.product.name}'"
            )
            raise ValueError(f"Invalid status: {new_status}")

        item.status = new_status
        item.save(update_fields=["status"])
        logger.info(
            f"Purchase Return Item '{item.product.name}' status updated to '{new_status}'."
        )
        return item
