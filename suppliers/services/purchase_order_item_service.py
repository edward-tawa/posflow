from suppliers.models.purchase_order_item_model import PurchaseOrderItem
from suppliers.models.purchase_order_model import PurchaseOrder
from loguru import logger
from django.db import transaction as db_transaction


class PurchaseOrderItemService:
    """
    Service class for managing purchase order items without using kwargs.
    """

    ALLOWED_STATUSES = {"DRAFT", "ORDERED", "RECEIVED", "CANCELLED"}

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def create_item(
        purchase_order: PurchaseOrder,
        product,
        quantity: int,
        unit_price: float,
        product_category=None
    ) -> PurchaseOrderItem:
        item = PurchaseOrderItem.objects.create(
            purchase_order=purchase_order,
            product=product,
            quantity=quantity,
            unit_price=unit_price,

            product_category=product_category or getattr(product, 'product_category', None)
        )
        logger.info(
            f"Purchase Order Item '{item.product.name}' created for order "
            f"'{purchase_order.reference_number}'."
        )
        PurchaseOrderItemService.add_to_order(item, purchase_order)
        logger.info(
            f"Purchase Order Item '{item.product.name}' added to order "
            f"'{purchase_order.reference_number}'."
        )
        return item

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_item(
        item: PurchaseOrderItem,
        quantity: int = None,
        unit_price: float = None,
        total_amount: float = None
    ) -> PurchaseOrderItem:
        updated = False
        if quantity is not None and item.quantity != quantity:
            item.quantity = quantity
            updated = True
        if unit_price is not None and item.unit_price != unit_price:
            item.unit_price = unit_price
            updated = True
        if total_amount is not None and item.total_amount != total_amount:
            item.total_amount = total_amount
            updated = True

        if updated:
            item.save(update_fields=['quantity', 'unit_price', 'total_amount'])
            logger.info(f"Purchase Order Item '{item.product.name}' updated.")

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
        name = item.product.name
        item.delete()
        logger.info(f"Purchase Order Item '{name}' deleted.")

        if order:
            order.update_total_amount()

    # -------------------------
    # ATTACH / DETACH
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def add_to_order(item: PurchaseOrderItem, order: PurchaseOrder) -> PurchaseOrderItem:
        previous_order = item.purchase_order
        item.purchase_order = order
        item.save(update_fields=['purchase_order'])
        logger.info(
            f"Purchase Order Item '{item.product.name}' attached to order "
            f"'{order.reference_number}' (previous: "
            f"'{previous_order.reference_number if previous_order else 'None'}')."
        )
        if previous_order:
            previous_order.update_total_amount()
        order.update_total_amount()
        return item

    @staticmethod
    @db_transaction.atomic
    def remove_from_order(item: PurchaseOrderItem) -> PurchaseOrderItem:
        previous_order = item.purchase_order
        item.purchase_order = None
        item.save(update_fields=['purchase_order'])
        logger.info(
            f"Purchase Order Item '{item.product.name}' detached from order "
            f"'{previous_order.reference_number if previous_order else 'None'}'."
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
            raise ValueError(f"Invalid status: {new_status}")
        item.status = new_status
        item.save(update_fields=['status'])
        logger.info(f"Purchase Order Item '{item.product.name}' status updated to '{new_status}'.")
        return item
