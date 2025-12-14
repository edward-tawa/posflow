from sales.models.sales_invoice_item_model import SalesInvoiceItem
from sales.models.sales_invoice_model import SalesInvoice
from django.db import transaction as db_transaction
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from loguru import logger


class SalesInvoiceItemService:

    @staticmethod
    @db_transaction.atomic
    def create_sales_invoice_item(**kwargs) -> SalesInvoiceItem:
        try:
            item = SalesInvoiceItem.objects.create(**kwargs)
            logger.info(
                f"Sales Invoice Item '{item.id}' created for invoice '{item.sales_invoice.invoice_number}'."
            )
            # Update totals automatically
            SalesInvoiceItemService.update_invoice_totals(item.sales_invoice)
            return item
        except Exception as e:
            logger.error(f"Error creating sales invoice item: {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def update_sales_invoice_item(item: SalesInvoiceItem, **kwargs) -> SalesInvoiceItem:
        try:
            for key, value in kwargs.items():
                setattr(item, key, value)
            item.save(update_fields=kwargs.keys())
            logger.info(f"Sales Invoice Item '{item.id}' updated.")
            # Update totals automatically
            SalesInvoiceItemService.update_invoice_totals(item.sales_invoice)
            return item
        except Exception as e:
            logger.error(f"Error updating sales invoice item '{item.id}': {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def delete_sales_invoice_item(item: SalesInvoiceItem) -> None:
        try:
            invoice = item.sales_invoice
            item_id = item.id
            item.delete()
            logger.info(f"Sales Invoice Item '{item_id}' deleted.")
            # Update totals automatically
            if invoice:
                SalesInvoiceItemService.update_invoice_totals(invoice)
        except Exception as e:
            logger.error(f"Error deleting sales invoice item '{item.id}': {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def attach_to_invoice(item: SalesInvoiceItem, invoice: SalesInvoice) -> SalesInvoiceItem:
        try:
            item.sales_invoice = invoice
            item.save(update_fields=["sales_invoice"])
            logger.info(
                f"Sales Invoice Item '{item.id}' attached to invoice '{invoice.invoice_number}'."
            )
            # Update totals automatically
            SalesInvoiceItemService.update_invoice_totals(invoice)
            return item
        except Exception as e:
            logger.error(
                f"Error attaching sales invoice item '{item.id}' to invoice '{invoice.invoice_number}': {str(e)}"
            )
            raise

    @staticmethod
    @db_transaction.atomic
    def calculate_totals(item: SalesInvoiceItem) -> dict:
        subtotal = item.subtotal
        tax = item.tax_amount
        total = item.total_price
        return {"subtotal": subtotal, "tax": tax, "total": total}

    @staticmethod
    @db_transaction.atomic
    def update_invoice_totals(invoice: SalesInvoice) -> SalesInvoice:
        total_amount = sum(item.subtotal + item.tax_amount for item in invoice.items.all())
        invoice.total_amount = total_amount
        invoice.save(update_fields=['total_amount'])
        logger.info(f"Updated totals for Sales Invoice '{invoice.invoice_number}' to {total_amount}")
        return invoice

    @staticmethod
    @db_transaction.atomic
    def mark_invoice_as_paid(invoice: SalesInvoice) -> SalesInvoice:
        invoice.status = 'PAID'
        invoice.paid_at = timezone.now()
        invoice.save(update_fields=['status', 'paid_at'])
        logger.info(f"Marked Sales Invoice '{invoice.invoice_number}' as PAID.")
        return invoice

    @staticmethod
    @db_transaction.atomic
    def bulk_create_sales_invoice_items(items_data: list, invoice: SalesInvoice) -> list:
        """
        Creates multiple SalesInvoiceItems and updates the invoice totals automatically.
        """
        try:
            items = [SalesInvoiceItem(**data, sales_invoice=invoice) for data in items_data]
            created_items = SalesInvoiceItem.objects.bulk_create(items)
            logger.info(f"Bulk created {len(created_items)} sales invoice items for invoice '{invoice.invoice_number}'.")
            # Update invoice totals after bulk creation
            SalesInvoiceItemService.update_invoice_totals(invoice)
            return created_items
        except Exception as e:
            logger.error(f"Error bulk creating sales invoice items for invoice '{invoice.invoice_number}': {str(e)}")
            raise
