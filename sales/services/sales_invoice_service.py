from sales.models.sales_invoice_model import SalesInvoice
from sales.models.sales_receipt_model import SalesReceipt
from accounts.models.sales_account_model import SalesAccount
from accounts.services.sales_account_service import SalesAccountService
from sales.services.sales_invoice_item_service import SalesInvoiceItemService
from inventory.services.product_stock_service import ProductStockService
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
        discount_amount=Decimal('0.00'),
        notes=None,
        issued_by=None
    ) -> SalesInvoice:
        """
        Creates a new SalesInvoice, deducts stock for all items, and records necessary transactions.
        """
        try:

            # Create the SalesInvoice
            sales_invoice = SalesInvoice.objects.create(
                company=company,
                branch=branch,
                customer=customer,
                sale=sale,
                sales_order=sales_order,
                discount_amount=discount_amount,
                notes=notes,
                issued_by=issued_by
            )


            # Get or create sales account
            sales_account = SalesAccountService.get_or_create_sales_account(
                company=sales_invoice.company,
                branch=sales_invoice.branch
            )

            logger.info(f"Sales Invoice '{sales_invoice.invoice_number}' created for company '{sales_invoice.company.name}'.")


            # Create the transaction
            transaction = TransactionService.create_transaction(
                company=sales_invoice.company,
                branch=sales_invoice.branch,
                debit_account=sales_invoice.customer.customer_account.account,
                credit_account=sales_account.account,
                transaction_type='SALES_INVOICE',
                transaction_category='SALES',
                total_amount=Decimal(sales_invoice.total_amount),
                customer=sales_invoice.customer,
                supplier=None,
            )

            # Apply transaction
            TransactionService.apply_transaction_to_accounts(transaction)
            logger.info(f"Transaction '{transaction.transaction_number}' created for Sales Invoice '{sales_invoice.invoice_number}'.")

            return sales_invoice

        except Exception as e:
            logger.error(f"Error creating sales invoice: {str(e)}")
            raise


    @staticmethod
    @db_transaction.atomic
    def update_sales_invoice(
        invoice: SalesInvoice,
        customer=None,
        sales_order=None,
        sale=None,
        receipt=None,
        discount_amount=None,
        notes=None,
        status=None,
        issued_by=None,
        updated_products: list = None  # List of dicts with item_id and new quantity/unit_price/tax_rate
    ) -> SalesInvoice:
        """
        Updates fields of a SalesInvoice and optionally adjusts invoice items.
        - Updates invoice fields explicitly.
        - Updates invoice item quantities and recalculates totals.
        """
        try:
            update_fields = []

            if customer is not None:
                invoice.customer = customer
                update_fields.append("customer")

            if sales_order is not None:
                invoice.sales_order = sales_order
                update_fields.append("sales_order")

            if sale is not None:
                invoice.sale = sale
                update_fields.append("sale")

            if receipt is not None:
                invoice.receipt = receipt
                update_fields.append("receipt")

            if discount_amount is not None:
                invoice.discount_amount = discount_amount
                update_fields.append("discount_amount")

            if notes is not None:
                invoice.notes = notes
                update_fields.append("notes")

            if status is not None:
                invoice.status = status
                update_fields.append("status")

            if issued_by is not None:
                invoice.issued_by = issued_by
                update_fields.append("issued_by")

            # Save invoice updates
            if update_fields:
                invoice.save(update_fields=update_fields)
                logger.info(f"Sales Invoice '{invoice.invoice_number}' updated: {update_fields}")

            # Update invoice items if provided
            for product in updated_products or []:
                item_id = product.get("item_id")
                new_quantity = product.get("quantity")
                new_unit_price = product.get("unit_price")
                new_tax_rate = product.get("tax_rate")

                item = invoice.items.get(id=item_id)

                # Calculate quantity difference for stock adjustment
                if new_quantity is not None and new_quantity != item.quantity:
                    diff = new_quantity - item.quantity
                    item.quantity = new_quantity
                    # Adjust stock by the difference
                    ProductStockService.adjust_stock_manually(
                        product=item.product,
                        company=invoice.company,
                        branch=invoice.branch,
                        quantity_change=diff,
                        reason=f"Sales Invoice '{invoice.invoice_number}' item quantity update"
                    )

                # Update other fields
                SalesInvoiceItemService.update_sales_invoice_item(
                    item=item,
                    quantity=item.quantity,
                    unit_price=new_unit_price,
                    tax_rate=new_tax_rate
                )

            # Recalculate total after all item updates
            invoice.update_total_amount()

            return invoice

        except Exception as e:
            logger.error(f"Error updating sales invoice '{invoice.invoice_number}': {str(e)}")
            raise

    @staticmethod
    def get_sales_invoice_by_invoice_number(invoice_number: str) -> SalesInvoice:
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
    def delete_sales_invoice(invoice: SalesInvoice) -> None:
        """
        Docstring for delete_sales_invoice
        Delete a sales invoice.
        1. Delete the SalesInvoice.
        2. Log the deletion.
        3. Handle exceptions.
        """
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



