from suppliers.models.supplier_credit_note_item_model import SupplierCreditNoteItem
from suppliers.models.supplier_credit_note_model import SupplierCreditNote
from suppliers.models.supplier_model import Supplier
from django.db import transaction
from loguru import logger


class SupplierCreditNoteItemService:
    """
    Service layer for Supplier Credit Note Item domain operations.
    """

    ALLOWED_STATUSES = {"DRAFT", "CONFIRMED", "CANCELLED"}

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def create_supplier_credit_note_item(**kwargs) -> SupplierCreditNoteItem:
        # Ensure quantity and unit_price are valid
        quantity = kwargs.get("quantity", 1)
        unit_price = kwargs.get("unit_price", 0.0)
        if quantity < 0 or unit_price < 0:
            raise ValueError("Quantity and unit price must be non-negative")

        kwargs["total_price"] = quantity * unit_price
        item = SupplierCreditNoteItem.objects.create(**kwargs)
        logger.info(f"Credit note item created | id={item.id}")
        return item

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_supplier_credit_note_item(
        item: SupplierCreditNoteItem,
        **kwargs
    ) -> SupplierCreditNoteItem:
        ALLOWED_UPDATE_FIELDS = {"description", "quantity", "unit_price"}
        for field, value in kwargs.items():
            if field in ALLOWED_UPDATE_FIELDS:
                if field == "quantity" or field == "unit_price":
                    if value < 0:
                        raise ValueError(f"{field} must be non-negative")
                setattr(item, field, value)

        # Recalculate total_price if quantity or unit_price changed
        if "quantity" in kwargs or "unit_price" in kwargs:
            item.total_price = item.quantity * item.unit_price

        item.save()
        logger.info(f"Credit note item updated | id={item.id}")
        return item

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def delete_supplier_credit_note_item(item: SupplierCreditNoteItem) -> None:
        item_id = item.id
        item.delete()
        logger.info(f"Credit note item deleted | id={item_id}")

    # -------------------------
    # RELATION MANAGEMENT
    # -------------------------
    @staticmethod
    @transaction.atomic
    def attach_to_credit_note(
        item: SupplierCreditNoteItem,
        credit_note: SupplierCreditNote
    ) -> SupplierCreditNoteItem:
        item.supplier_credit_note = credit_note
        item.save(update_fields=['supplier_credit_note'])
        logger.info(
            f"Credit note item '{item.id}' attached to credit note '{credit_note.id}'."
        )
        return item

    @staticmethod
    @transaction.atomic
    def detach_from_credit_note(item: SupplierCreditNoteItem) -> SupplierCreditNoteItem:
        item.supplier_credit_note = None
        item.save(update_fields=['supplier_credit_note'])
        logger.info(f"Credit note item '{item.id}' detached from its credit note.")
        return item

    # -------------------------
    # STATUS MANAGEMENT
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_supplier_credit_note_item_status(
        item: SupplierCreditNoteItem,
        new_status: str
    ) -> SupplierCreditNoteItem:
        if new_status not in SupplierCreditNoteItemService.ALLOWED_STATUSES:
            logger.error(
                f"Attempted to set invalid status '{new_status}' for credit note item '{item.id}'."
            )
            raise ValueError(f"Invalid status: {new_status}")

        item.status = new_status
        item.save(update_fields=['status'])
        logger.info(f"Credit note item '{item.id}' status updated to '{new_status}'.")
        return item

    # -------------------------
    # QUANTITY & PRICE UPDATES
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_supplier_credit_note_item_quantity(
        item: SupplierCreditNoteItem,
        new_quantity: int
    ) -> SupplierCreditNoteItem:
        if new_quantity < 0:
            raise ValueError("Quantity must be non-negative")

        item.quantity = new_quantity
        item.total_price = item.quantity * item.unit_price
        item.save(update_fields=['quantity', 'total_price'])
        logger.info(f"Credit note item '{item.id}' quantity updated to '{new_quantity}'.")
        return item

    @staticmethod
    @transaction.atomic
    def update_supplier_credit_note_item_unit_price(
        item: SupplierCreditNoteItem,
        new_unit_price: float
    ) -> SupplierCreditNoteItem:
        if new_unit_price < 0:
            raise ValueError("Unit price must be non-negative")

        item.unit_price = new_unit_price
        item.total_price = item.quantity * item.unit_price
        item.save(update_fields=['unit_price', 'total_price'])
        logger.info(f"Credit note item '{item.id}' unit price updated to '{new_unit_price}'.")
        return item
