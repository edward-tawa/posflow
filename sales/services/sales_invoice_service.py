from sales.models.sales_invoice_model import SalesInvoice
from sales.models.sales_receipt_model import SalesReceipt
from accounts.models.sales_account_model import SalesAccount
from accounts.services.sales_account_service import SalesAccountService
from sales.services.sales_invoice_item_service import SalesInvoiceItemService
from django.db import transaction as db_transaction
from transactions.services.transaction_service import TransactionService
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from loguru import logger


class SalesInvoiceService:
    
    @staticmethod
    @db_transaction.atomic
    def create_sales_invoice(
        company,
        branch,
        customer,
        sale=None,
        sales_order=None,
        receipt=None,
        discount_amount=Decimal('0.00'),
        notes=None,
        issued_by=None
    ) -> SalesInvoice:
        """
        Creates a new SalesInvoice, deducts stock, and records necessary transactions.
        """
        try:
            # Create the invoice
            invoice = SalesInvoice.objects.create(
                company=company,
                branch=branch,
                customer=customer,
                sale=sale,
                sales_order=sales_order,
                receipt=receipt,
                discount_amount=discount_amount,
                notes=notes,
                issued_by=issued_by
            )

            # Get or create sales account
            sales_account = SalesAccountService.get_or_create_sales_account(
                company=invoice.company,
                branch=invoice.branch
            )
            logger.info(f"Sales Invoice '{invoice.invoice_number}' created for company '{invoice.company.name}'.")
            # Add items from the sales order to the invoice
            SalesInvoiceItemService.add_order_items_to_invoice(sales_order, invoice)
            # Deduct stock for the items in the invoice
            SalesInvoiceService.deduct_stock_from_invoice(invoice)

            # Create the transaction
            transaction = TransactionService.create_transaction(
                company=invoice.company,
                branch=invoice.branch,
                debit_account=invoice.customer.customer_account.account,
                credit_account=sales_account.account,
                transaction_type='SALES_INVOICE',
                transaction_category='SALES',
                total_amount=Decimal(invoice.total_amount),
                customer=invoice.customer,
                supplier=None,
            )

            # Apply transaction
            TransactionService.apply_transaction_to_accounts(transaction)
            logger.info(f"Transaction '{transaction.transaction_number}' created for Sales Invoice '{invoice.invoice_number}'.")

            return invoice

        except Exception as e:
            logger.error(f"Error creating sales invoice: {str(e)}")
            raise
    
    @staticmethod
    @db_transaction.atomic
    def get_sales_invoice_by_number(invoice_number: str) -> SalesInvoice:
        try:
            invoice = SalesInvoice.objects.get(invoice_number=invoice_number)
            return invoice
        except SalesInvoice.DoesNotExist:
            logger.warning(f"Sales Invoice with number '{invoice_number}' does not exist.")
            return None
        except Exception as e:
            logger.error(f"Error retrieving sales invoice '{invoice_number}': {str(e)}")
            return None
    
    @staticmethod
    def get_sales_invoices_by_customer(customer):
        try:
            invoices = SalesInvoice.objects.filter(customer=customer).order_by('-created_at')
            return invoices
        except Exception as e:
            logger.error(f"Error retrieving sales invoices for customer '{customer}': {str(e)}")
            return None

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
    def deduct_stock_from_invoice(invoice: SalesInvoice) -> None:
        """
        Deducts stock for all products in a given sales invoice.
        
        :param invoice: SalesInvoice instance
        """
        try:
            for item in invoice.items.all():
                product = item.product
                if product.stock < item.quantity:
                    raise ValueError(
                        f"Not enough stock for product '{product.name}'. "
                        f"Available: {product.stock}, Required: {item.quantity}"
                    )
                product.stock -= item.quantity
                product.save(update_fields=['stock'])
                logger.info(
                    f"Deducted {item.quantity} from stock of '{product.name}'. "
                    f"New stock: {product.stock}"
                )
            logger.info(f"Stock updated for all items in invoice '{invoice.invoice_number}'")
        except Exception as e:
            logger.error(f"Error deducting stock for invoice '{invoice.invoice_number}': {str(e)}")
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
        # Restore stock before marking invoice as voided
        SalesInvoiceService.restore_stock_for_invoice(invoice)
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
    

    @staticmethod
    @db_transaction.atomic
    def restore_stock_for_invoice(invoice: SalesInvoice) -> None:
        """
        Restores stock for all products in a given sales invoice.
        Useful if an invoice is voided or deleted.
        
        :param invoice: SalesInvoice instance
        """
        try:
            for item in invoice.items.all():
                product = item.product
                product.stock += item.quantity
                product.save(update_fields=['stock'])
                logger.info(
                    f"Restored {item.quantity} to stock of '{product.name}'. "
                    f"New stock: {product.stock}"
                )
            logger.info(f"Stock restored for all items in invoice '{invoice.invoice_number}'")
        except Exception as e:
            logger.error(f"Error restoring stock for invoice '{invoice.invoice_number}': {str(e)}")
            raise

    

