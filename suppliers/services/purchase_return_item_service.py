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
    ALLOWED_UPDATE_FIELDS = {"product_name", "quantity", "unit_price", "notes"}

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def create_item(**kwargs) -> PurchaseReturnItem:
        quantity = kwargs.get("quantity", 1)
        unit_price = kwargs.get("unit_price", 0.0)
        if quantity < 0 or unit_price < 0:
            raise ValueError("Quantity and unit price must be non-negative")

        kwargs["total_price"] = quantity * unit_price
        item = PurchaseReturnItem.objects.create(**kwargs)
        logger.info(
            f"Purchase Return Item '{item.product_name}' created for return "
            f"'{item.purchase_return.id if item.purchase_return else 'None'}'."
        )
        return item

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_item(item: PurchaseReturnItem, **kwargs) -> PurchaseReturnItem:
        for key, value in kwargs.items():
            if key not in PurchaseReturnItemService.ALLOWED_UPDATE_FIELDS:
                logger.warning(f"Ignored invalid update field '{key}' for item '{item.product_name}'")
                continue

            if key in {"quantity", "unit_price"} and value < 0:
                raise ValueError(f"{key} must be non-negative")

            setattr(item, key, value)

        # Recalculate total_price if quantity or unit_price changed
        if "quantity" in kwargs or "unit_price" in kwargs:
            item.total_price = item.quantity * item.unit_price

        item.save()
        logger.info(
            f"Purchase Return Item '{item.product_name}' updated in return "
            f"'{item.purchase_return.id if item.purchase_return else 'None'}'."
        )
        return item

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_item(item: PurchaseReturnItem) -> None:
        return_id = item.purchase_return.id if item.purchase_return else 'None'
        item_name = item.product_name
        item.delete()
        logger.info(f"Deleted Purchase Return Item '{item_name}' from return '{return_id}'.")

    # -------------------------
    # RELATION MANAGEMENT
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def attach_to_return(item: PurchaseReturnItem, purchase_return: PurchaseReturn) -> PurchaseReturnItem:
        previous_return = item.purchase_return
        item.purchase_return = purchase_return
        item.save(update_fields=['purchase_return'])

        if previous_return and previous_return != purchase_return:
            previous_return.update_total_amount()
        purchase_return.update_total_amount()

        logger.info(
            f"Purchase Return Item '{item.product_name}' attached to return '{purchase_return.id}' "
            f"(previous return: '{previous_return.id if previous_return else 'None'}')."
        )
        return item

    @staticmethod
    @db_transaction.atomic
    def detach_from_return(item: PurchaseReturnItem) -> PurchaseReturnItem:
        previous_return = item.purchase_return
        item.purchase_return = None
        item.save(update_fields=['purchase_return'])

        if previous_return:
            previous_return.update_total_amount()

        logger.info(
            f"Purchase Return Item '{item.product_name}' detached from return "
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
                f"Attempted to set invalid status '{new_status}' for item '{item.product_name}'"
            )
            raise ValueError(f"Invalid status: {new_status}")

        item.status = new_status
        item.save(update_fields=["status"])
        logger.info(
            f"Purchase Return Item '{item.product_name}' status updated to '{new_status}'."
        )
        return item
