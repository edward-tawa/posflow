from sales.models.sales_invoice_item_model import SalesInvoiceItem
from sales.models.sales_invoice_model import SalesInvoice
from django.db import transaction as db_transaction
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from loguru import logger
from sales.models.sales_order_model import SalesOrder
from sales.services.sales_receipt_item_service import SalesReceiptItemService


class SalesInvoiceItemService:

    @staticmethod
    @db_transaction.atomic
    def create_sales_invoice_item(
        sales_invoice: SalesInvoice,
        product,
        product_name: str,
        quantity: int,
        unit_price: Decimal,
        tax_rate: Decimal
    ) -> SalesInvoiceItem:
        """
        Creates a single SalesInvoiceItem and updates the invoice totals.
        """
        try:
            item = SalesInvoiceItem.objects.create(
                sales_invoice=sales_invoice,
                product=product,
                product_name=product_name,
                quantity=quantity,
                unit_price=unit_price,
                tax_rate=tax_rate
            )
            logger.info(
                f"Sales Invoice Item '{item.id}' created for invoice '{item.sales_invoice.invoice_number}'."
            )
            SalesInvoiceItemService.update_invoice_totals(sales_invoice)
            return item
        except Exception as e:
            logger.error(f"Error creating sales invoice item: {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def update_sales_invoice_item(
        item: SalesInvoiceItem,
        product=None,
        product_name: str | None = None,
        quantity: int | None = None,
        unit_price: Decimal | None = None,
        tax_rate: Decimal | None = None
    ) -> SalesInvoiceItem:
        """
        Updates fields of a SalesInvoiceItem explicitly.
        """
        try:
            update_fields = []

            if product is not None:
                item.product = product
                update_fields.append("product")
            if product_name is not None:
                item.product_name = product_name
                update_fields.append("product_name")
            if quantity is not None:
                item.quantity = quantity
                update_fields.append("quantity")
            if unit_price is not None:
                item.unit_price = unit_price
                update_fields.append("unit_price")
            if tax_rate is not None:
                item.tax_rate = tax_rate
                update_fields.append("tax_rate")

            if update_fields:
                item.save(update_fields=update_fields)
                logger.info(f"Sales Invoice Item '{item.id}' updated: {update_fields}")
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
    def get_total_quantity(invoice: SalesInvoice) -> int:
        """
        Returns the total quantity of all items in the invoice
        """
        return sum(item.quantity for item in invoice.items.all())


    @staticmethod
    @db_transaction.atomic
    def add_sales_invoice_item_to_invoice(item: SalesInvoiceItem, invoice: SalesInvoice) -> SalesInvoiceItem:
        try:
            item.sales_invoice = invoice
            item.save(update_fields=["sales_invoice"])
            logger.info(
                f"Sales Invoice Item '{item.id}' added to invoice '{invoice.invoice_number}'."
            )
            return item
        except Exception as e:
            logger.error(
                f"Error adding sales invoice item '{item.id}' to invoice '{invoice.invoice_number}': {str(e)}"
            )
            raise
    
    @staticmethod
    @db_transaction.atomic
    def add_sales_invoice_items_to_invoice(items: list[SalesInvoiceItem], invoice: SalesInvoice) -> None:
        try:
            for item in items:
                item.sales_invoice = invoice
                item.save(update_fields=["sales_invoice"])
            logger.info(
                f"Added {len(items)} items to Sales Invoice '{invoice.invoice_number}'."
            )
        except Exception as e:
            logger.error(
                f"Error adding items to sales invoice '{invoice.invoice_number}': {str(e)}"
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

    
    @staticmethod
    @db_transaction.atomic
    def add_order_items_to_invoice(sales_order: SalesOrder, sales_invoice: SalesInvoice):
        for order_item in sales_order.items.all():
            SalesInvoiceItemService.create_sales_invoice_item(
                sales_invoice=sales_invoice,
                product=order_item.product,
                product_name=order_item.product_name,
                quantity=order_item.quantity,
                unit_price=order_item.unit_price,
                tax_rate=order_item.tax_rate
            )
        logger.info(f"Added {sales_order.items.count()} items from Order '{sales_order.order_number}' to Invoice '{sales_invoice.invoice_number}'.")


    