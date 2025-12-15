from sales.models.sales_payment_model import SalesPayment
from django.db import transaction as db_transaction
from loguru import logger



class SalesPaymentService:
    """
    Service class for handling sales payment operations.
    """

    @staticmethod
    @db_transaction.atomic
    def create_sales_payment(sales_order, sales_receipt, payment, amount):
        """
        Applies a payment to a sales order and receipt.
        Ensures atomicity of the operation.
        """
        try:
            sales_payment = SalesPayment.objects.create(
                sales_order=sales_order,
                sales_receipt=sales_receipt,
                payment=payment,
                amount_applied=amount
            )
            logger.info(f"Applied payment {payment.payment_number} to order {sales_order.order_number} and receipt {sales_receipt.receipt_number} for amount {amount}.")
            return sales_payment
        except Exception as e:
            logger.error(f"Failed to apply payment {payment.payment_number} to order {sales_order.order_number} and receipt {sales_receipt.receipt_number}: {e}")
            raise
    
    @staticmethod
    @db_transaction.atomic
    def delete_sales_payment(sales_payment):
        """
        Reverses a previously applied sales payment.
        Ensures atomicity of the operation.
        """
        try:
            sales_payment.delete()
        except Exception as e:
            logger.error(f"Failed to reverse payment {sales_payment.payment.payment_number} from order {sales_payment.sales_order.order_number} and receipt {sales_payment.sales_receipt.receipt_number}: {e}")
            raise
    

    @staticmethod
    def get_payments_for_order(sales_order):
        """
        Retrieves all payments applied to a specific sales order.
        """
        payments = SalesPayment.objects.filter(sales_order=sales_order)
        logger.info(f"Retrieved {payments.count()} payments for order {sales_order.order_number}.")
        return payments
    
    
    @staticmethod
    def get_payments_for_receipt(sales_receipt):
        """
        Retrieves all payments applied to a specific sales receipt.
        """
        payments = SalesPayment.objects.filter(sales_receipt=sales_receipt)
        logger.info(f"Retrieved {payments.count()} payments for receipt {sales_receipt.receipt_number}.")
        return payments
    

    @staticmethod
    @db_transaction.atomic
    def update_sales_payment(sales_payment, new_amount):
        """
        Updates the amount applied in a sales payment.
        Ensures atomicity of the operation.
        """
        try:
            sales_payment.amount_applied = new_amount
            sales_payment.save()
            logger.info(f"Updated payment {sales_payment.payment.payment_number} for order {sales_payment.sales_order.order_number} to new amount {new_amount}.")
            return sales_payment
        except Exception as e:
            logger.error(f"Failed to update payment {sales_payment.payment.payment_number} for order {sales_payment.sales_order.order_number}: {e}")
            raise