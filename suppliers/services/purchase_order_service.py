from suppliers.models.purchase_order_model import PurchaseOrder
from suppliers.services.purchase_order_item_service import PurchaseOrderItemService
from suppliers.models.supplier_model import Supplier
from loguru import logger
from django.db import transaction as db_transaction
from typing import List, Dict, Optional
from datetime import date


class PurchaseOrderService:
    """
    Service class for managing purchase orders.
    """

    ALLOWED_STATUSES = {"DRAFT", "APPROVED", "RECEIVED", "CANCELLED"}

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def create_order(
        company,
        supplier,
        quantity: int,
        total_amount: float,
        order_date: date = None,
        delivery_date: date = None,
        status: str = "DRAFT",
        reference_number: str = None,
        notes: str = None
    ) -> PurchaseOrder:
        if status not in PurchaseOrderService.ALLOWED_STATUSES:
            raise ValueError(f"Invalid status: {status}")

        order = PurchaseOrder.objects.create(
            company=company,
            supplier=supplier,
            quantity_ordered=quantity,
            total_amount=total_amount,
            order_date=order_date or date.today(),
            delivery_date=delivery_date,
            status=status,
            reference_number=reference_number,
            notes=notes
        )

        logger.info(
            f"Purchase Order '{order.id}' created for supplier "
            f"'{order.supplier.name}' with status '{order.status}'."
        )
    
        return order

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_order(
        order: PurchaseOrder,
        quantity_ordered: int = None,
        total_amount: float = None,
        delivery_date: date = None,
        status: str = None,
        notes: str = None
    ) -> PurchaseOrder:
        updated = False

        if quantity_ordered is not None and order.quantity_ordered != quantity_ordered:
            order.quantity_ordered = quantity_ordered
            updated = True
        if total_amount is not None and order.total_amount != total_amount:
            order.total_amount = total_amount
            updated = True
        if delivery_date is not None and order.delivery_date != delivery_date:
            order.delivery_date = delivery_date
            updated = True
        if status is not None:
            if status not in PurchaseOrderService.ALLOWED_STATUSES:
                raise ValueError(f"Invalid status: {status}")
            if order.status != status:
                order.status = status
                updated = True
        if notes is not None and order.notes != notes:
            order.notes = notes
            updated = True

        if updated:
            order.save(update_fields=[f for f, v in [
                ('quantity_ordered', quantity_ordered),
                ('total_amount', total_amount),
                ('delivery_date', delivery_date),
                ('status', status),
                ('notes', notes)
            ] if v is not None])
            order.update_total_amount()
            logger.info(f"Purchase Order '{order.id}' updated.")
        else:
            logger.info(f"No changes applied to Purchase Order '{order.id}'.")

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
        logger.info(f"Purchase Order '{order.id}' attached to supplier '{supplier.id}'.")
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
            raise ValueError(f"Invalid status: {new_status}")
        order.status = new_status
        order.save(update_fields=['status'])
        logger.info(f"Purchase Order '{order.id}' status updated to '{new_status}'.")
        return order

    @staticmethod
    @db_transaction.atomic
    def approve_order(order: PurchaseOrder) -> PurchaseOrder:
        if order.status != "DRAFT":
            raise ValueError("Only DRAFT orders can be approved.")
        order.status = "APPROVED"
        order.save(update_fields=['status'])
        logger.info(f"Purchase Order '{order.id}' approved.")
        return order
