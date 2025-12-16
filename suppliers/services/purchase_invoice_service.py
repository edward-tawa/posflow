from suppliers.models.purchase_invoice_model import PurchaseInvoice
from suppliers.models.supplier_model import Supplier
from loguru import logger
from django.db import transaction as db_transaction


class PurchaseInvoiceService:
    """
    Service class for managing purchase invoices.
    Provides methods for CRUD operations, supplier association,
    and status management with business rules enforced.
    """

    ALLOWED_STATUSES = {"DRAFT", "APPROVED", "PAID", "CANCELLED"}
    ALLOWED_UPDATE_FIELDS = {"invoice_date", "due_date", "status", "notes"}

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def create_invoice(**kwargs) -> PurchaseInvoice:
        status = kwargs.get("status", "DRAFT")
        if status not in PurchaseInvoiceService.ALLOWED_STATUSES:
            raise ValueError(f"Invalid status: {status}")
        kwargs["status"] = status

        invoice = PurchaseInvoice.objects.create(**kwargs)
        logger.info(
            f"Purchase Invoice '{invoice.id}' created for supplier "
            f"'{invoice.supplier.name if invoice.supplier else 'None'}' with status '{invoice.status}'."
        )
        return invoice

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_invoice(invoice: PurchaseInvoice, **kwargs) -> PurchaseInvoice:
        fields_to_update = []
        for key, value in kwargs.items():
            if key not in PurchaseInvoiceService.ALLOWED_UPDATE_FIELDS:
                logger.warning(f"Ignored invalid update field '{key}' for invoice '{invoice.id}'")
                continue
            if key == "status" and value not in PurchaseInvoiceService.ALLOWED_STATUSES:
                raise ValueError(f"Invalid status: {value}")
            setattr(invoice, key, value)
            fields_to_update.append(key)

        invoice.save(update_fields=fields_to_update)
        logger.info(
            f"Purchase Invoice '{invoice.id}' updated for supplier "
            f"'{invoice.supplier.name if invoice.supplier else 'None'}'."
        )
        return invoice

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_invoice(invoice: PurchaseInvoice) -> None:
        invoice_id = invoice.id
        invoice.delete()
        logger.info(f"Purchase Invoice '{invoice_id}' deleted.")

    # -------------------------
    # SUPPLIER MANAGEMENT
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def attach_to_supplier(invoice: PurchaseInvoice, supplier: Supplier) -> PurchaseInvoice:
        previous_supplier = invoice.supplier
        invoice.supplier = supplier
        invoice.save(update_fields=['supplier'])
        logger.info(
            f"Invoice '{invoice.id}' attached to supplier '{supplier.name}' "
            f"(previous supplier: '{previous_supplier.name if previous_supplier else 'None'}')."
        )
        return invoice

    @staticmethod
    @db_transaction.atomic
    def detach_from_supplier(invoice: PurchaseInvoice) -> PurchaseInvoice:
        previous_supplier = invoice.supplier
        invoice.supplier = None
        invoice.save(update_fields=['supplier'])
        logger.info(
            f"Invoice '{invoice.id}' detached from supplier "
            f"'{previous_supplier.name if previous_supplier else 'None'}'."
        )
        return invoice

    # -------------------------
    # STATUS MANAGEMENT
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_invoice_status(invoice: PurchaseInvoice, new_status: str) -> PurchaseInvoice:
        if new_status not in PurchaseInvoiceService.ALLOWED_STATUSES:
            logger.error(
                f"Attempted to set invalid status '{new_status}' for invoice '{invoice.id}'"
            )
            raise ValueError(f"Invalid status: {new_status}")

        invoice.status = new_status
        invoice.save(update_fields=['status'])
        logger.info(f"Purchase Invoice '{invoice.id}' status updated to '{new_status}'.")
        return invoice

    # -------------------------
    # HELPER METHODS
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def approve_invoice(invoice: PurchaseInvoice) -> PurchaseInvoice:
        if invoice.status != "DRAFT":
            logger.error(f"Cannot approve invoice '{invoice.id}' with status '{invoice.status}'.")
            raise ValueError("Only DRAFT invoices can be approved.")
        invoice.status = "APPROVED"
        invoice.save(update_fields=['status'])
        logger.info(f"Purchase Invoice '{invoice.id}' approved.")
        return invoice