from sales.models.sales_order_model import SalesOrder
from sales.models.sales_receipt_model import SalesReceipt
from sales.services.sales_receipt_item_service import SalesReceiptItemService
from transactions.services.transaction_service import TransactionService
from accounts.services.cash_account_service import CashAccountService
from inventory.services.product_stock_service import ProductStockService
from customers.models.customer_model import Customer
from sales.models.sale_model import Sale
from django.db import transaction as db_transaction
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from typing import Union
from loguru import logger


class SalesReceiptService:

    
    @staticmethod
    @db_transaction.atomic
    def create_sales_receipt(
        sale: Sale,
        sales_order: SalesOrder,
        customer,
        branch,
        company,
        issued_by,
        total_amount,
        notes: str = ""
    ) -> SalesReceipt:
        """
        Creates a new SalesReceipt for a CASH sale and records the corresponding cash transaction.
        """

        if sale.sale_type != 'CASH':
            raise ValueError("Sales Receipt can only be created for CASH sales.")

        try:
            # Create the sales receipt
            receipt = SalesReceipt.objects.create(
                sale=sale,
                sales_order=sales_order,
                customer=customer,
                branch=branch,
                company=company,
                issued_by=issued_by,
                total_amount=total_amount,
                notes=notes
            )

            logger.info(f"Sales Receipt '{receipt.receipt_number}' created for company '{receipt.company.name}'.")

            # Prepare accounts and transaction
            debit_account = CashAccountService.get_or_create_cash_account(company=company, branch=branch)
            
            transaction = TransactionService.create_transaction(
                company=company,
                branch=branch,
                debit_account=debit_account,
                credit_account=customer.account,
                transaction_type='CASH_SALE',
                transaction_category='SALES',
                total_amount=receipt.total_amount,
                customer=customer,
                supplier=None,
            )

            # Apply transaction to accounts
            TransactionService.apply_transaction_to_accounts(transaction)
            logger.info(f"Transaction '{transaction.transaction_number}' created for Sales Receipt '{receipt.receipt_number}'.")

            return receipt, sales_order

        except Exception as e:
            logger.error(f"Error creating sales receipt: {str(e)}")
            raise


    @staticmethod
    @db_transaction.atomic
    def update_sales_receipt(
        receipt: SalesReceipt,
        customer: Customer = None,
        branch = None,
        company = None,
        sale: Sale = None,
        sales_order: SalesOrder = None,
        total_amount: Decimal = None,
        notes: str = None,
        status: str = None,
        issued_by = None
    ) -> SalesReceipt:
        """
        Update a SalesReceipt with provided fields.
        Only non-None arguments will be applied.
        """
        try:
            update_fields = []

            if customer is not None:
                receipt.customer = customer
                update_fields.append('customer')

            if branch is not None:
                receipt.branch = branch
                update_fields.append('branch')

            if company is not None:
                receipt.company = company
                update_fields.append('company')

            if sale is not None:
                receipt.sale = sale
                update_fields.append('sale')

            if sales_order is not None:
                receipt.sales_order = sales_order
                update_fields.append('sales_order')

            if total_amount is not None:
                receipt.total_amount = total_amount
                update_fields.append('total_amount')

            if notes is not None:
                receipt.notes = notes
                update_fields.append('notes')

            if status is not None:
                receipt.status = status
                update_fields.append('status')

            if issued_by is not None:
                receipt.issued_by = issued_by
                update_fields.append('issued_by')

            if update_fields:
                receipt.save(update_fields=update_fields)
                logger.info(f"Sales Receipt '{receipt.receipt_number}' updated: {update_fields}")

            return receipt

        except Exception as e:
            logger.error(f"Error updating sales receipt '{receipt.receipt_number}': {str(e)}")
            raise


    
    @staticmethod
    @db_transaction.atomic
    def delete_sales_receipt(receipt: SalesReceipt) -> None:
        util_receipt = receipt
        try:
            # Restore stock for all items first
            for item in receipt.items.all():
                ProductStockService.increase_stock_for_voided_sale_item(item)
            # Delete items and receipt
            receipt.delete()
            logger.info(f"Sales Receipt '{util_receipt.receipt_number}' and its items deleted, stock restored.")
        except Exception as e:
            logger.error(f"Error deleting sales receipt '{util_receipt.receipt_number}': {str(e)}")
            raise



    @staticmethod
    @db_transaction.atomic
    def void_sales_receipt(receipt: SalesReceipt, reason: str = "") -> SalesReceipt:
        if receipt.is_voided:
            logger.warning(f"Receipt '{receipt.receipt_number}' is already voided.")
            return receipt

        try:
            # Loop through all items and restore stock individually
            for item in receipt.items.all():
                ProductStockService.increase_stock_for_voided_sale_item(item)

            # Mark receipt as voided
            receipt.is_voided = True
            receipt.void_reason = reason
            receipt.voided_at = timezone.now()
            receipt.status = 'VOIDED'
            receipt.save(update_fields=["is_voided", "void_reason", "voided_at", "status"])

            logger.warning(f"Sales receipt '{receipt.receipt_number}' voided. Reason: {reason}")
            return receipt

        except Exception as e:
            logger.error(f"Error voiding sales receipt '{receipt.receipt_number}': {str(e)}")
            raise

    

    @staticmethod
    @db_transaction.atomic
    def attach_sales_receipt_to_sale(receipt: SalesReceipt, sale) -> SalesReceipt:
        receipt.sale = sale
        receipt.save(update_fields=["sale"])
        logger.info(
            f"Receipt '{receipt.receipt_number}' attached to sale '{sale.sale_number}'."
        )
        return receipt
    

    @staticmethod
    @db_transaction.atomic
    def update_sales_receipt_status(receipt: SalesReceipt, new_status: str) -> SalesReceipt:
        try:
            receipt.status = new_status
            receipt.save(update_fields=["status"])
            logger.info(f"Updated status for Sales Receipt '{receipt.receipt_number}' to '{new_status}'.")
            return receipt
        except Exception as e:
            logger.error(f"Error updating status for Sales Receipt '{receipt.receipt_number}': {str(e)}")
            raise
    


    @staticmethod
    def get_sales_receipt_by_id(receipt_id: int) -> SalesReceipt | None:
        try:
            return SalesReceipt.objects.select_related(
                'sale', 'company', 'branch'
            ).get(id=receipt_id)
        except SalesReceipt.DoesNotExist:
            logger.warning(f"Sales Receipt with id '{receipt_id}' not found.")
            return None
    
    @staticmethod
    def get_sales_receipts_by_customer(customer: Union[Customer, int]):
        return SalesReceipt.objects.filter(customer=customer).order_by('-created_at')
