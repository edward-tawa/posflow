from sales.models.sales_order_model import SalesOrder
from sales.models.sales_receipt_model import SalesReceipt
from sales.services.sales_receipt_item_service import SalesReceiptItemService
from transactions.services.transaction_service import TransactionService
from accounts.services.cash_account_service import CashAccountService
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

            # Add items from the sales order to the receipt
            SalesReceiptItemService.add_order_items_to_receipt(sales_order, receipt)

            # Deduct stock for the items in the receipt
            SalesReceiptService.deduct_stock_from_receipt(receipt)

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

            return receipt

        except Exception as e:
            logger.error(f"Error creating sales receipt: {str(e)}")
            raise


    @staticmethod
    @db_transaction.atomic
    def update_sales_receipt(receipt: SalesReceipt, **kwargs) -> SalesReceipt:
        try:
            for key, value in kwargs.items():
                setattr(receipt, key, value)
            receipt.save(update_fields=kwargs.keys())
            logger.info(f"Sales Receipt '{receipt.receipt_number}' updated.")
            return receipt
        except Exception as e:
            logger.error(f"Error updating sales receipt '{receipt.receipt_number}': {str(e)}")
            raise

    
    @staticmethod
    @db_transaction.atomic
    def delete_sales_receipt(receipt: SalesReceipt) -> None:
        try:
            receipt_number = receipt.receipt_number
            receipt.delete()
            logger.info(f"Sales Receipt '{receipt_number}' deleted.")
        except Exception as e:
            logger.error(f"Error deleting sales receipt '{receipt.receipt_number}': {str(e)}")
            raise


    @staticmethod
    @db_transaction.atomic
    def deduct_stock_from_receipt(receipt: SalesReceipt) -> None:
        """
        Deducts stock for all products in a given sales receipt.
        """
        try:
            for item in receipt.items.all():
                product = item.product
                if product.stock < item.quantity:
                    raise ValueError(
                        f"Not enough stock for product '{product.name}'."
                        f"Available: {product.stock}, Required: {item.quantity}"
                    )
                product.stock -= item.quantity
                product.save(update_fields=['stock'])
                logger.info(
                    f"Deducted {item.quantity} from stock of '{product.name}'. "
                    f"New stock: {product.stock}"
                )
            logger.info(f"Stock updated for all items in receipt '{receipt.receipt_number}'")
        except Exception as e:
            logger.error(f"Error deducting stock for receipt '{receipt.receipt_number}': {str(e)}")
            raise


    @staticmethod
    @db_transaction.atomic
    def void_receipt(receipt: SalesReceipt, reason: str = "") -> SalesReceipt:
        if receipt.is_voided:
            logger.warning(f"Receipt '{receipt.receipt_number}' is already voided.")
            return receipt
        # Restore stock before marking receipt as voided
        SalesReceiptService.restore_stock_for_receipt(receipt)
        receipt.is_voided = True
        receipt.void_reason = reason
        receipt.voided_at = timezone.now()
        receipt.status = 'VOIDED'
        receipt.save(update_fields=["is_voided", "void_reason", "voided_at", "status"])
        logger.warning(f"Sales receipt '{receipt.receipt_number}' voided. Reason: {reason}")
        return receipt
    

    @staticmethod
    @db_transaction.atomic
    def attach_to_sale(receipt: SalesReceipt, sale) -> SalesReceipt:
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
    @db_transaction.atomic
    def update_total_amount(receipt: SalesReceipt) -> SalesReceipt:
        """
        Recalculate the total amount for the receipt based on its items.
        """
        total = sum(
            (item.subtotal + item.tax_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            for item in receipt.items.all()
        )
        receipt.total_amount = total
        receipt.save(update_fields=['total_amount'])
        logger.info(f"Updated total amount for receipt '{receipt.receipt_number}' to {total}")
        return receipt


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


    @staticmethod
    @db_transaction.atomic
    def restore_stock_for_receipt(receipt: SalesReceipt) -> None:
        """
        Restores stock for all products in a given sales receipt.
        Used when a receipt is voided or reversed.
        """
        try:
            for item in receipt.items.all():
                product = item.product
                product.stock += item.quantity
                product.save(update_fields=['stock'])

                logger.info(
                    f"Restored {item.quantity} to stock of '{product.name}'. "
                    f"New stock: {product.stock}"
                )

            logger.info(f"Stock restored for receipt '{receipt.receipt_number}'")

        except Exception as e:
            logger.error(
                f"Error restoring stock for receipt '{receipt.receipt_number}': {str(e)}"
            )
            raise
