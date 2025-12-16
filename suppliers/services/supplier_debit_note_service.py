from suppliers.models.supplier_model import Supplier
from suppliers.models.supplier_debit_note_model import SupplierDebitNote
from django.db import transaction, IntegrityError
from django.utils import timezone
from loguru import logger
from typing import Optional


class SupplierDebitNoteService:
    """
    Service layer for Supplier Debit Note domain operations.
    """

    ALLOWED_STATUS_TRANSITIONS = {
        "DRAFT": {"SENT", "CANCELLED"},
        "SENT": {"PAID", "OVERDUE", "CANCELLED"},
        "OVERDUE": {"PAID", "CANCELLED"},
        "PAID": set(),
        "CANCELLED": set(),
    }

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def create_supplier_debit_note(**kwargs) -> SupplierDebitNote:
        debit_note = SupplierDebitNote.objects.create(**kwargs)
        logger.info(f"Supplier Debit Note created | id={debit_note.id}")
        return debit_note

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_supplier_debit_note(
        debit_note: SupplierDebitNote,
        **kwargs
    ) -> SupplierDebitNote:
        for field, value in kwargs.items():
            setattr(debit_note, field, value)

        debit_note.save()
        logger.info(f"Supplier Debit Note updated | id={debit_note.id}")
        return debit_note

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def delete_supplier_debit_note(debit_note: SupplierDebitNote) -> None:
        debit_note_id = debit_note.id
        debit_note.delete()
        logger.info(f"Supplier Debit Note deleted | id={debit_note_id}")

    # -------------------------
    # RELATION MANAGEMENT
    # -------------------------
    @staticmethod
    @transaction.atomic
    def attach_to_supplier(
        debit_note: SupplierDebitNote,
        supplier: Supplier
    ) -> SupplierDebitNote:
        debit_note.supplier = supplier
        debit_note.save(update_fields=["supplier"])
        logger.info(
            f"Debit note attached to supplier | debit_note_id={debit_note.id}, supplier_id={supplier.id}"
        )
        return debit_note

    @staticmethod
    @transaction.atomic
    def detach_from_supplier(debit_note: SupplierDebitNote) -> SupplierDebitNote:
        debit_note.supplier = None
        debit_note.save(update_fields=["supplier"])
        logger.info(f"Debit note detached from supplier | id={debit_note.id}")
        return debit_note

    # -------------------------
    # STATUS MANAGEMENT
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_status(
        debit_note: SupplierDebitNote,
        new_status: str
    ) -> SupplierDebitNote:
        current_status = debit_note.status

        allowed = SupplierDebitNoteService.ALLOWED_STATUS_TRANSITIONS.get(
            current_status, set()
        )

        if new_status not in allowed:
            raise ValueError(
                f"Invalid status transition: {current_status} → {new_status}"
            )

        debit_note.status = new_status

        if new_status == "PAID":
            debit_note.paid_at = timezone.now()
            debit_note.save(update_fields=["status", "paid_at"])
        else:
            debit_note.save(update_fields=["status"])

        logger.info(
            f"Debit note status updated | id={debit_note.id}, {current_status} → {new_status}"
        )
        return debit_note
