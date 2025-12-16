from suppliers.models.purchase_return_model import PurchaseReturn
from suppliers.models.supplier_model import Supplier
from loguru import logger
from django.db import transaction as db_transaction


class PurchaseReturnService:
    """
    Service class for managing purchase returns.
    Provides methods for creating, updating, and deleting purchase returns.
    Includes detailed logging and business rule enforcement.
    """

    ALLOWED_STATUSES = {"DRAFT", "APPROVED", "CANCELLED"}
    ALLOWED_UPDATE_FIELDS = {"reference", "date", "notes", "total_amount"}

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def create_purchase_return(**kwargs) -> PurchaseReturn:
        try:
            status = kwargs.get("status", "DRAFT")
            if status not in PurchaseReturnService.ALLOWED_STATUSES:
                raise ValueError(f"Invalid status: {status}")

            purchase_return = PurchaseReturn.objects.create(**kwargs)
            logger.info(f"Purchase Return '{purchase_return.id}' created.")
            return purchase_return
        except Exception as e:
            logger.error(f"Error creating purchase return: {str(e)}")
            raise

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_purchase_return(purchase_return: PurchaseReturn, **kwargs) -> PurchaseReturn:
        try:
            for key, value in kwargs.items():
                if key in PurchaseReturnService.ALLOWED_UPDATE_FIELDS:
                    setattr(purchase_return, key, value)
                else:
                    logger.warning(f"Attempted to update invalid field '{key}' on purchase return '{purchase_return.id}'")

            # Optional: recalculate total_amount here if linked items exist
            # purchase_return.total_amount = sum(item.total_price for item in purchase_return.items.all())

            purchase_return.save(update_fields=kwargs.keys())
            logger.info(f"Purchase Return '{purchase_return.id}' updated.")
            return purchase_return
        except Exception as e:
            logger.error(f"Error updating purchase return '{purchase_return.id}': {str(e)}")
            raise

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_purchase_return(purchase_return: PurchaseReturn) -> None:
        try:
            pr_id = purchase_return.id
            purchase_return.delete()
            logger.info(f"Purchase Return '{pr_id}' deleted.")
        except Exception as e:
            logger.error(f"Error deleting purchase return '{purchase_return.id}': {str(e)}")
            raise

    # -------------------------
    # STATUS MANAGEMENT
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_purchase_return_status(purchase_return: PurchaseReturn, new_status: str) -> PurchaseReturn:
        if new_status not in PurchaseReturnService.ALLOWED_STATUSES:
            logger.error(f"Attempted to set invalid status '{new_status}' for purchase return '{purchase_return.id}'")
            raise ValueError(f"Invalid status: {new_status}")

        purchase_return.status = new_status
        purchase_return.save(update_fields=["status"])
        logger.info(f"Purchase Return '{purchase_return.id}' status updated to '{new_status}'.")
        return purchase_return

    # -------------------------
    # RELATION MANAGEMENT
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def attach_to_supplier(
        purchase_return: PurchaseReturn,
        supplier: Supplier
    ) -> PurchaseReturn:
        previous_supplier = purchase_return.supplier
        purchase_return.supplier = supplier
        purchase_return.save(update_fields=['supplier'])
        logger.info(
            f"Purchase Return '{purchase_return.id}' attached to supplier '{supplier.name}' "
            f"(previous supplier: '{previous_supplier.name if previous_supplier else 'None'}')."
        )
        return purchase_return

    @staticmethod
    @db_transaction.atomic
    def detach_from_supplier(purchase_return: PurchaseReturn) -> PurchaseReturn:
        previous_supplier = purchase_return.supplier
        purchase_return.supplier = None
        purchase_return.save(update_fields=['supplier'])
        logger.info(
            f"Purchase Return '{purchase_return.id}' detached from supplier"
            f"'{previous_supplier.name if previous_supplier else 'None'}'."
        )
        return purchase_return