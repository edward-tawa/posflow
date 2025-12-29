from suppliers.models.supplier_credit_note_model import SupplierCreditNote
from suppliers.models.supplier_model import Supplier
from django.db import transaction
from loguru import logger


class SupplierCreditNoteService:
    """
    Service layer for Supplier Credit Note domain operations.
    """

    ALLOWED_STATUSES = {"DRAFT", "CONFIRMED", "CANCELLED"}

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def create_supplier_credit_note(**kwargs) -> SupplierCreditNote:
        credit_note = SupplierCreditNote.objects.create(**kwargs)
        logger.info(f"Credit note created | id={credit_note.id}")
        return credit_note

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_supplier_credit_note(
        credit_note: SupplierCreditNote,
        **kwargs
    ) -> SupplierCreditNote:
        # Optional: restrict to allowed fields
        ALLOWED_UPDATE_FIELDS = {"reference", "date", "notes", "amount"}
        for field, value in kwargs.items():
            if field in ALLOWED_UPDATE_FIELDS:
                setattr(credit_note, field, value)

        credit_note.save()
        logger.info(f"Credit note updated | id={credit_note.id}")
        return credit_note

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def delete_supplier_credit_note(credit_note: SupplierCreditNote) -> None:
        credit_note_id = credit_note.id
        credit_note.delete()
        logger.info(f"Credit note deleted | id={credit_note_id}")

    # -------------------------
    # RELATION MANAGEMENT
    # -------------------------
    @staticmethod
    @transaction.atomic
    def attach_to_supplier(
        credit_note: SupplierCreditNote,
        supplier: Supplier
    ) -> SupplierCreditNote:
        credit_note.supplier = supplier
        credit_note.save(update_fields=['supplier'])
        logger.info(
            f"Credit note '{credit_note.id}' attached to supplier '{supplier.id}'."
        )
        return credit_note

    @staticmethod
    @transaction.atomic
    def detach_from_supplier(credit_note: SupplierCreditNote) -> SupplierCreditNote:
        credit_note.supplier = None
        credit_note.save(update_fields=['supplier'])
        logger.info(f"Credit note '{credit_note.id}' detached from supplier.")
        return credit_note

    # -------------------------
    # STATUS MANAGEMENT
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_supplier_credit_note_status(
        credit_note: SupplierCreditNote,
        new_status: str
    ) -> SupplierCreditNote:
        if new_status not in SupplierCreditNoteService.ALLOWED_STATUSES:
            logger.error(
                f"Attempted to set invalid status '{new_status}' for credit note '{credit_note.id}'."
            )
            raise ValueError(f"Invalid status: {new_status}")

        credit_note.status = new_status
        credit_note.save(update_fields=['status'])
        logger.info(
            f"Credit note '{credit_note.id}' status updated to '{new_status}'."
        )
        return credit_note
    


    