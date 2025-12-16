from suppliers.models.supplier_debit_note_model import SupplierDebitNote
from suppliers.models.supplier_debit_note_item_model import SupplierDebitNoteItem
from django.db import transaction
from loguru import logger



class SupplierDebitNoteItemService:
    """
    Service layer for Supplier Debit Note Item domain operations.
    """

    ALLOWED_STATUSES = {"DRAFT", "CONFIRMED", "CANCELLED"}

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def create_supplier_debit_note_item(**kwargs) -> SupplierDebitNoteItem:
        item = SupplierDebitNoteItem.objects.create(**kwargs)
        logger.info(f"Debit note item created | id={item.id}")
        return item

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_supplier_debit_note_item(
        item: SupplierDebitNoteItem,
        **kwargs
    ) -> SupplierDebitNoteItem:
        for field, value in kwargs.items():
            setattr(item, field, value)

        item.save()
        logger.info(f"Debit note item updated | id={item.id}")
        return item

    
    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def delete_supplier_debit_note_item(item: SupplierDebitNoteItem) -> None:
        item_id = item.id
        item.delete()
        logger.info(f"Debit note item deleted | id={item_id}")

    # -------------------------
    # RELATION MANAGEMENT
    # -------------------------
    @staticmethod
    @transaction.atomic
    def attach_to_debit_note(
        item: SupplierDebitNoteItem,
        debit_note: SupplierDebitNote
    ) -> SupplierDebitNoteItem:
        item.supplier_debit_note = debit_note
        item.save(update_fields=["supplier_debit_note"])
        logger.info(
            f"Debit note item attached | item_id={item.id}, debit_note_id={debit_note.id}"
        )
        return item

    @staticmethod
    @transaction.atomic
    def detach_from_debit_note(item: SupplierDebitNoteItem) -> SupplierDebitNoteItem:
        item.supplier_debit_note = None
        item.save(update_fields=["supplier_debit_note"])
        logger.info(f"Debit note item detached | item_id={item.id}")
        return item

    @staticmethod
    @transaction.atomic
    def attach_to_product(
        item: SupplierDebitNoteItem,
        product
    ) -> SupplierDebitNoteItem:
        item.product = product
        item.save(update_fields=["product"])
        logger.info(
            f"Debit note item attached to product | item_id={item.id}, product_id={product.id}"
        )
        return item

    @staticmethod
    @transaction.atomic
    def detach_from_product(item: SupplierDebitNoteItem) -> SupplierDebitNoteItem:
        item.product = None
        item.save(update_fields=["product"])
        logger.info(f"Debit note item detached from product | item_id={item.id}")
        return item

    # -------------------------
    # STATUS MANAGEMENT
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_status(
        item: SupplierDebitNoteItem,
        new_status: str
    ) -> SupplierDebitNoteItem:
        if new_status not in SupplierDebitNoteItemService.ALLOWED_STATUSES:
            raise ValueError(f"Invalid debit note item status: {new_status}")

        item.status = new_status
        item.save(update_fields=["status"])
        logger.info(
            f"Debit note item status updated | item_id={item.id}, status={new_status}"
        )
        return item
