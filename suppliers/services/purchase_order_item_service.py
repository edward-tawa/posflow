from suppliers.models.purchase_order_item_model import PurchaseOrderItem
from suppliers.models.purchase_order_model import PurchaseOrder
from loguru import logger
from django.db import transaction as db_transaction


class PurchaseOrderItemService:
    """
    Service class for managing purchase order items.
    Provides methods for creating, updating, deleting items,
    attaching/detaching them to/from purchase orders,
    with automatic order total updates and detailed logging.
    """

    ALLOWED_UPDATE_FIELDS = {"product_name", "quantity", "unit_price", "total_price", "notes"}
    ALLOWED_STATUSES = {"DRAFT", "ORDERED", "RECEIVED", "CANCELLED"}

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def create_item(**kwargs) -> PurchaseOrderItem:
        item = PurchaseOrderItem.objects.create(**kwargs)
        logger.info(
            f"Purchase Order Item '{item.product_name}' created for order "
            f"'{item.purchase_order.order_number if item.purchase_order else 'None'}'."
        )
        # Update order total if linked
        if item.purchase_order:
            item.purchase_order.update_total_amount()
        return item

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_item(item: PurchaseOrderItem, **kwargs) -> PurchaseOrderItem:
        for key, value in kwargs.items():
            if key in PurchaseOrderItemService.ALLOWED_UPDATE_FIELDS:
                setattr(item, key, value)
        item.save(update_fields=[k for k in kwargs if k in PurchaseOrderItemService.ALLOWED_UPDATE_FIELDS])
        logger.info(f"Purchase Order Item '{item.product_name}' updated.")

        if item.purchase_order:
            item.purchase_order.update_total_amount()
        return item

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_item(item: PurchaseOrderItem) -> None:
        order = item.purchase_order
        item_name = item.product_name
        item.delete()
        logger.info(f"Purchase Order Item '{item_name}' deleted.")

        if order:
            order.update_total_amount()

    # -------------------------
    # ATTACH / DETACH
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def attach_to_order(item: PurchaseOrderItem, order: PurchaseOrder) -> PurchaseOrderItem:
        previous_order = item.purchase_order
        item.purchase_order = order
        item.save(update_fields=['purchase_order'])
        logger.info(
            f"Purchase Order Item '{item.product_name}' attached to order "
            f"'{order.order_number}' (previous order: "
            f"'{previous_order.order_number if previous_order else 'None'}')."
        )
        if previous_order:
            previous_order.update_total_amount()
        order.update_total_amount()
        return item

    @staticmethod
    @db_transaction.atomic
    def detach_from_order(item: PurchaseOrderItem) -> PurchaseOrderItem:
        previous_order = item.purchase_order
        item.purchase_order = None
        item.save(update_fields=['purchase_order'])
        logger.info(
            f"Purchase Order Item '{item.product_name}' detached from order "
            f"'{previous_order.order_number if previous_order else 'None'}'."
        )
        if previous_order:
            previous_order.update_total_amount()
        return item

    # -------------------------
    # STATUS MANAGEMENT
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_item_status(item: PurchaseOrderItem, new_status: str) -> PurchaseOrderItem:
        if new_status not in PurchaseOrderItemService.ALLOWED_STATUSES:
            logger.error(f"Invalid status '{new_status}' for item '{item.product_name}'")
            raise ValueError(f"Invalid status: {new_status}")

        item.status = new_status
        item.save(update_fields=["status"])
        logger.info(f"Purchase Order Item '{item.product_name}' status updated to '{new_status}'.")
        return item
