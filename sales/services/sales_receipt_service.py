from sales.models.sales_receipt_model import SalesReceipt
from django.db import transaction as db_transaction
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from loguru import logger


class SalesReceiptService:

    @staticmethod
    @db_transaction.atomic
    def create_sales_receipt(**kwargs) -> SalesReceipt:
        try:
            receipt = SalesReceipt.objects.create(**kwargs)
            logger.info(
                f"Sales Receipt '{receipt.receipt_number}' created for company '{receipt.company.name}'."
            )
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
    def void_receipt(receipt: SalesReceipt, reason: str = "") -> SalesReceipt:
        if receipt.is_voided:
            logger.warning(f"Receipt '{receipt.receipt_number}' is already voided.")
            return receipt
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
