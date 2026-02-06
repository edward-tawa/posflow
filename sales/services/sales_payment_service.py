# from sales.models.sales_payment_model import SalesPayment
# from django.db import transaction as db_transaction
# from sales.models.sales_receipt_model import SalesReceipt
# from transactions.services.transaction_service import TransactionService
# from accounts.services.customer_account_service import CustomerAccountService
# from accounts.services.cash_account_service import CashAccountService
# from sales.models.sale_model import Sale
# from loguru import logger



# class SalesPaymentService:
#     """
#     Service class for handling sales payment operations.
#     """

#     @staticmethod
#     @db_transaction.atomic
#     def create_sales_payment(sales_order, sale, payment, amount):
#         """
#         Applies a payment to a CREDIT sale.
#         Records the corresponding cash → AR transaction.
#         """
#         try:
#             # Allocation record (non-accounting)
#             sales_payment = SalesPayment.objects.create(
#                 sales_order=sales_order,
#                 sale=sale,
#                 payment=payment,
#                 amount_applied=amount
#             )

#             # Accounts
#             customer_account = CustomerAccountService.get_or_create_customer_account(
#                 customer=sales_order.customer,
#                 company=sales_order.company,
#                 branch=sales_order.branch
#             )

#             cash_account = CashAccountService.get_or_create_cash_account(
#                 company=sales_order.company,
#                 branch=sales_order.branch
#             )

#             # Payment transaction (THIS is the accounting event)
#             transaction = TransactionService.create_transaction(
#                 company=sales_order.company,
#                 branch=sales_order.branch,
#                 debit_account=cash_account,
#                 credit_account=customer_account,
#                 transaction_type='CUSTOMER_PAYMENT',
#                 transaction_category='RECEIPT',
#                 total_amount=amount,
#                 customer=sales_order.customer,
#             )

#             TransactionService.apply_transaction_to_accounts(transaction)

#             sales_receipt = SalesPaymentService.create_payment_receipt(
#                 payment=payment,
#                 sale=sale,
#                 customer=sales_order.customer,
#                 branch=sales_order.branch,
#                 company=sales_order.company,
#                 issued_by=payment.issued_by,
#                 amount=amount
#             )

#             sales_payment.sales_receipt = sales_receipt
#             sales_payment.save()

#             logger.info(
#                 f"Customer payment {payment.payment_number} applied to Sale "
#                 f"{sale.sale_number} for amount {amount}."
#             )

#             return sales_payment

#         except Exception as e:
#             logger.error(
#                 f"Failed to apply payment {payment.payment_number} "
#                 f"to order {sales_order.order_number}: {e}"
#             )
#             raise
            
    

    
#     @staticmethod
#     @db_transaction.atomic
#     def create_payment_receipt(payment, sale, customer, branch, company, issued_by, amount):
#         receipt = SalesReceipt.objects.create(
#             sale=sale,
#             customer=customer,
#             branch=branch,
#             company=company,
#             issued_by=issued_by,
#             total_amount=amount,
#             receipt_type='PAYMENT',
#             notes=f"Payment receipt for {payment.payment_number}"
#         )

#         logger.info(
#             f"Payment receipt '{receipt.receipt_number}' created for "
#             f"payment '{payment.payment_number}' amount {amount}."
#         )

#         return receipt

    

#     @staticmethod
#     def get_payments_for_order(sales_order):
#         """
#         Retrieves all payments applied to a specific sales order.
#         """
#         payments = SalesPayment.objects.filter(sales_order=sales_order)
#         logger.info(f"Retrieved {payments.count()} payments for order {sales_order.order_number}.")
#         return payments
    

    

#     @staticmethod
#     @db_transaction.atomic
#     def update_sales_payment(sales_payment, new_amount):
#         """
#         Updates the amount applied in a sales payment.
#         Ensures atomicity of the operation.
#         """
#         try:
#             sales_payment.amount_applied = new_amount
#             sales_payment.save()
#             logger.info(f"Updated payment {sales_payment.payment.payment_number} for order {sales_payment.sales_order.order_number} to new amount {new_amount}.")
#             return sales_payment
#         except Exception as e:
#             logger.error(f"Failed to update payment {sales_payment.payment.payment_number} for order {sales_payment.sales_order.order_number}: {e}")
#             raise