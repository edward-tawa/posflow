from suppliers.models.purchase_invoice_model import PurchaseInvoice
from suppliers.models.supplier_model import Supplier
from loguru import logger
from django.db import transaction as db_transaction
from suppliers.services.purchase_invoice_item_service import PurchaseInvoiceItemService
from datetime import datetime
from users.models import User
from company.models import Company
from branch.models import Branch
from suppliers.models.purchase_order_model import PurchaseOrder
from suppliers.models.purchase_model import Purchase


class PurchaseInvoiceService:
    """
    Service class for managing purchase invoices without kwargs.
    """

    ALLOWED_STATUSES = {"DRAFT", "APPROVED", "PAID", "CANCELLED"}

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def create_invoice(
        company: Company,
        branch: Branch,
        supplier: Supplier,
        invoice_date: datetime = None,
        purchase: Purchase = None,
        purchase_order: PurchaseOrder = None,
        issued_by: User = None,
        total_amount: float = 0,
        balance: float = 0,
        status: str = "DRAFT"
    ) -> PurchaseInvoice:
        if status not in PurchaseInvoiceService.ALLOWED_STATUSES:
            raise ValueError(f"Invalid status: {status}")

        purchase_invoice = PurchaseInvoice.objects.create(
            company=company,
            branch=branch,
            supplier=supplier,
            invoice_date=invoice_date or datetime.now(),
            purchase=purchase,
            purchase_order=purchase_order,
            issued_by=issued_by,
            total_amount=total_amount,
            balance=balance,
            status=status
        )

        logger.info(
            f"Purchase Invoice '{purchase_invoice.invoice_number}' created for supplier "
            f"'{supplier.name}' with status '{status}'."
        )
        
        return purchase_invoice

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_invoice(
        invoice: PurchaseInvoice,
        invoice_date: datetime = None,
        purchase: Purchase = None,
        purchase_order: PurchaseOrder = None,
        issued_by: User = None,
        total_amount: float = None,
        balance: float = None,
        status: str = None
    ) -> PurchaseInvoice:
        updated_fields = []

        if invoice_date and invoice.invoice_date != invoice_date:
            invoice.invoice_date = invoice_date
            updated_fields.append('invoice_date')
        if purchase and invoice.purchase != purchase:
            invoice.purchase = purchase
            updated_fields.append('purchase')
        if purchase_order and invoice.purchase_order != purchase_order:
            invoice.purchase_order = purchase_order
            updated_fields.append('purchase_order')
        if issued_by and invoice.issued_by != issued_by:
            invoice.issued_by = issued_by
            updated_fields.append('issued_by')
        if total_amount is not None and invoice.total_amount != total_amount:
            invoice.total_amount = total_amount
            updated_fields.append('total_amount')
        if balance is not None and invoice.balance != balance:
            invoice.balance = balance
            updated_fields.append('balance')
        if status:
            if status not in PurchaseInvoiceService.ALLOWED_STATUSES:
                raise ValueError(f"Invalid status: {status}")
            if invoice.status != status:
                invoice.status = status
                updated_fields.append('status')

        if updated_fields:
            invoice.save(update_fields=updated_fields)
            logger.info(
                f"Purchase Invoice '{invoice.invoice_number}' updated for supplier "
                f"'{invoice.supplier.name if invoice.supplier else 'None'}'."
            )
            invoice.update_total_amount()
        else:
            logger.info(f"No changes applied to Purchase Invoice '{invoice.invoice_number}'.")

        return invoice

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_invoice(invoice: PurchaseInvoice) -> None:
        invoice_number = invoice.invoice_number
        invoice.delete()
        logger.info(f"Purchase Invoice '{invoice_number}' deleted.")

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
            f"Invoice '{invoice.invoice_number}' attached to supplier '{supplier.name}' "
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
            f"Invoice '{invoice.invoice_number}' detached from supplier "
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
            raise ValueError(f"Invalid status: {new_status}")

        invoice.status = new_status
        invoice.save(update_fields=['status'])
        logger.info(f"Purchase Invoice '{invoice.invoice_number}' status updated to '{new_status}'.")
        return invoice

    # -------------------------
    # HELPER METHODS
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def approve_invoice(invoice: PurchaseInvoice) -> PurchaseInvoice:
        if invoice.status != "DRAFT":
            raise ValueError(f"Cannot approve invoice '{invoice.invoice_number}' with status '{invoice.status}'.")
        invoice.status = "APPROVED"
        invoice.save(update_fields=['status'])
        logger.info(f"Purchase Invoice '{invoice.invoice_number}' approved.")
        return invoice
