from suppliers.models.purchase_order_model import PurchaseOrder
from suppliers.models.supplier_model import Supplier
from loguru import logger
from django.db import transaction as db_transaction



class PurchaseOrderService:
    """
    Service class for managing purchase orders.
    Provides methods for creating, updating, deleting orders,
    attaching/detaching them to/from suppliers,
    and status management with business rules enforced.
    """

    ALLOWED_STATUSES = {"DRAFT", "APPROVED", "RECEIVED", "CANCELLED"}
    ALLOWED_UPDATE_FIELDS = {"order_date", "delivery_date", "status", "notes"}

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def create_order(**kwargs) -> PurchaseOrder:
        # Validate initial status
        status = kwargs.get("status", "DRAFT")
        if status not in PurchaseOrderService.ALLOWED_STATUSES:
            raise ValueError(f"Invalid status: {status}")
        kwargs["status"] = status

        order = PurchaseOrder.objects.create(**kwargs)
        logger.info(
            f"Purchase Order '{order.id}' created for supplier "
            f"'{order.supplier.name if order.supplier else 'None'}' with status '{order.status}'."
        )
        return order
    

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_order(order: PurchaseOrder, **kwargs) -> PurchaseOrder:
        for key, value in kwargs.items():
            if key not in PurchaseOrderService.ALLOWED_UPDATE_FIELDS:
                logger.warning(f"Ignored invalid update field '{key}' for order '{order.id}'")
                continue

            if key == "status" and value not in PurchaseOrderService.ALLOWED_STATUSES:
                raise ValueError(f"Invalid status: {value}")

            setattr(order, key, value)

        order.save()
        logger.info(
            f"Purchase Order '{order.id}' updated for supplier "
            f"'{order.supplier.name if order.supplier else 'None'}'."
        )
        return order
    

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_order(order: PurchaseOrder) -> None:
        try:
            order_id = order.id
            order.delete()
            logger.info(f"Purchase Order '{order_id}' deleted.")
        except Exception as e:
            logger.error(f"Error deleting purchase order '{order.id}': {str(e)}")
            raise
    

    # -------------------------
    # RELATION MANAGEMENT
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def attach_to_supplier(order: PurchaseOrder, supplier: Supplier) -> PurchaseOrder:
        order.supplier = supplier
        order.save(update_fields=['supplier'])
        logger.info(
            f"Purchase Order '{order.id}' attached to supplier '{supplier.id}'."
        )
        return order
    


    @staticmethod
    @db_transaction.atomic
    def detach_from_supplier(order: PurchaseOrder) -> PurchaseOrder:
        order.supplier = None
        order.save(update_fields=['supplier'])
        logger.info(f"Purchase Order '{order.id}' detached from supplier.")
        return order
    

    # -------------------------
    # STATUS MANAGEMENT
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_order_status(order: PurchaseOrder, new_status: str) -> PurchaseOrder:
        if new_status not in PurchaseOrderService.ALLOWED_STATUSES:
            logger.error(
                f"Attempted to set invalid status '{new_status}' for order '{order.id}'"
            )
            raise ValueError(f"Invalid status: {new_status}")

        order.status = new_status
        order.save(update_fields=['status'])
        logger.info(
            f"Purchase Order '{order.id}' status updated to '{new_status}'."
        )
        return order
    


    @staticmethod
    @db_transaction.atomic
    def approve_order(order: PurchaseOrder) -> PurchaseOrder:
        if order.status != "DRAFT":
            logger.error(
                f"Cannot approve order '{order.id}' with status '{order.status}'."
            )
            raise ValueError("Only DRAFT orders can be approved.")

        order.status = "APPROVED"
        order.save(update_fields=['status'])
        logger.info(f"Purchase Order '{order.id}' approved.")
        return order