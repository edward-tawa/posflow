from sales.models.sales_invoice_model import SalesInvoice
from sales.models.sales_receipt_model import SalesReceipt
from django.db import transaction as db_transaction
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from loguru import logger



class SalesInvoiceService:
    
    @staticmethod
    @db_transaction.atomic
    def create_sales_invoice(**kwargs) -> SalesInvoice:
        try:
            invoice = SalesInvoice.objects.create(**kwargs)
            logger.info(
                f"Sales Invoice '{invoice.invoice_number}' created for company '{invoice.company.name}'."
            )
            return invoice
        except Exception as e:
            logger.error(f"Error creating sales invoice: {str(e)}")
            raise
    

    @staticmethod
    @db_transaction.atomic
    def update_sales_invoice(invoice: SalesInvoice, **kwargs) -> SalesInvoice:
        try:
            for key, value in kwargs.items():
                setattr(invoice, key, value)
            invoice.save(update_fields=kwargs.keys())
            logger.info(f"Sales Invoice '{invoice.invoice_number}' updated.")
            return invoice
        except Exception as e:
            logger.error(f"Error updating sales invoice '{invoice.invoice_number}': {str(e)}")
            raise
    

    @staticmethod
    @db_transaction.atomic
    def delete_sales_invoice(invoice: SalesInvoice) -> None:
        try:
            invoice_number = invoice.invoice_number
            invoice.delete()
            logger.info(f"Sales Invoice '{invoice_number}' deleted.")
        except Exception as e:
            logger.error(f"Error deleting sales invoice '{invoice.invoice_number}': {str(e)}")
            raise
    
    @staticmethod
    @db_transaction.atomic
    def update_sales_invoice_status(invoice: SalesInvoice, new_status: str) -> SalesInvoice:
        try:
            invoice.status = new_status
            invoice.save(update_fields=["status"])
            logger.info(f"Sales Invoice '{invoice.invoice_number}' status updated to '{new_status}'.")
            return invoice
        except Exception as e:
            logger.error(f"Error updating status for sales invoice '{invoice.invoice_number}': {str(e)}")
            raise
    
    @staticmethod
    @db_transaction.atomic
    def apply_discount(invoice: SalesInvoice, discount_amount: float) -> SalesInvoice:
        try:
            invoice.discount_amount = discount_amount
            invoice.total_amount = float(
                Decimal(invoice.total_amount - discount_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            )
            invoice.save(update_fields=["discount_amount", "total_amount"])
            logger.info(
                f"Applied discount of {discount_amount} to Sales Invoice '{invoice.invoice_number}'. New total amount: {invoice.total_amount}"
            )
            return invoice
        except Exception as e:
            logger.error(f"Error applying discount to sales invoice '{invoice.invoice_number}': {str(e)}")
            raise
    
    @staticmethod
    @db_transaction.atomic
    def attach_to_sale(invoice: SalesInvoice, sale) -> SalesInvoice:
        try:
            invoice.sale = sale
            invoice.save(update_fields=["sale"])
            logger.info(
                f"Sales Invoice '{invoice.invoice_number}' attached to sale '{sale.sale_number}'."
            )
            return invoice
        except Exception as e:
            logger.error(
                f"Error attaching sales invoice '{invoice.invoice_number}' to sale '{sale.sale_number}': {str(e)}"
            )
            raise

    
    @staticmethod
    @db_transaction.atomic
    def update_total_amount(invoice: SalesInvoice) -> SalesInvoice:
        total = sum(
            (item.subtotal + item.tax_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            for item in invoice.items.all()
        )
        invoice.total_amount = total - (invoice.discount_amount or 0)
        invoice.save(update_fields=['total_amount'])
        logger.info(f"Updated total amount for Sales Invoice '{invoice.invoice_number}' to {invoice.total_amount}")
        return invoice
    

    @staticmethod
    @db_transaction.atomic
    def void_invoice(invoice: SalesInvoice, reason: str = "") -> SalesInvoice:
        if getattr(invoice, "is_voided", False):
            logger.warning(f"Invoice '{invoice.invoice_number}' is already voided.")
            return invoice
        invoice.is_voided = True
        invoice.void_reason = reason
        invoice.voided_at = timezone.now()
        invoice.status = 'VOIDED'
        invoice.save(update_fields=["is_voided", "void_reason", "voided_at", "status"])
        logger.warning(f"Sales Invoice '{invoice.invoice_number}' voided. Reason: {reason}")
        return invoice
    


    @staticmethod
    @db_transaction.atomic
    def mark_as_issued(invoice: SalesInvoice) -> SalesInvoice:
        invoice.status = 'ISSUED'
        invoice.issued_at = timezone.now()
        invoice.save(update_fields=['status', 'issued_at'])
        logger.info(f"Sales Invoice '{invoice.invoice_number}' marked as ISSUED")
        return invoice