from company.models.company_model import Company
from branch.models.branch_model import Branch
from sales.models.sales_invoice_model import SalesInvoice
from sales.models.sales_order_model import SalesOrder
from sales.services.sale_service import SaleService
from customers.models.customer_model import Customer
from django.db import transaction as db_transaction
from payments.services.sales.sales_payment_service import SalesPaymentService
from payments.services.payment.payment_service import PaymentService
from sales.services.sales_receipt_service import SalesReceiptService
from sales.services.sales_receipt_item_service import SalesReceiptItemService
from transactions.services.transaction_service import TransactionService
from accounts.services.cash_account_service import CashAccountService
from accounts.services.sales_account_service import SalesAccountService
from loguru import logger
from users.models.user_model import User
from dataclasses import dataclass
from sales.models.sale_model import Sale
from payments.models.payment_model import Payment
from payments.models.sales_payment_model import SalesPayment
from transactions.models.transaction_model import Transaction
from sales.models.sales_receipt_model import SalesReceipt




@dataclass
class CheckoutResult:
    sale: Sale
    payment: Payment
    sales_payment: SalesPayment
    receipt: SalesReceipt | None


class PosCheckOutService:
    
    # Handles the checkout process for sales orders
    # There is no stock handling here, it is assumed to be handled elsewhere ealier in the flow
    # Here is where payment is processed and receipt generated

    @staticmethod
    @db_transaction.atomic
    def process_checkout(*,
                            company: Company, 
                            branch: Branch,
                            customer: Customer,  
                            payment_method: str,
                            sales_order: SalesOrder,
                            sales_receipt: SalesReceipt,
                            received_by: User,
                            sales_invoice: SalesInvoice = None,
                            ) -> CheckoutResult:
        """
        Process the checkout for a sales order.
        """
        try:
            # Placeholder for checkout logic
            logger.info("Processing checkout...")
            sale = SaleService.create_sale(
                company=company,
                branch=branch,
                customer=customer,
                sale_type = 'CASH',
                sales_order=sales_order,
                issued_by=received_by,
            )
            # create a general payment container
            payment = PaymentService.create_payment(
                company=company,
                branch=branch,
                paid_by=sales_order.customer,
                amount=sales_order.total_amount,
                method=payment_method,
                payment_type='incoming',  
            )

            sales_payment = SalesPaymentService.create_sales_payment(
                company=company,
                branch=branch,
                sales_order=sales_order,
                sales_invoice=sales_invoice,
                sales_receipt=sales_receipt,
                payment=payment,
                payment_method=payment_method,
                received_by=received_by,
            )


            # Record Transaction
            # create transaction
            # Prepare accounts and transaction
            debit_account = CashAccountService.get_or_create_cash_account(company=company, branch=branch)
            credit_account = SalesAccountService.get_or_create_sales_account(company=company, branch=branch)

            transaction = TransactionService.create_transaction(
                company=company,
                branch=branch,
                debit_account=debit_account,
                credit_account=credit_account,
                transaction_type='CASH_SALE',
                transaction_category='SALES',
                total_amount=sales_order.total_amount,
                customer=customer,
                supplier=None,
            )

            # Apply transaction to accounts
            TransactionService.apply_transaction_to_accounts(transaction)

            # create receipt
            sales_receipt = None 
            if sales_payment.payment.status == 'SUCCESS':
                sales_receipt = SalesReceiptService.create_sales_receipt(
                    sale=sale,
                    sales_order=sales_order,
                    customer=customer,
                    branch=branch,
                    company=company,
                    issued_by=received_by,
                    total_amount=sales_order.total_amount,
                    notes="Receipt generated upon successful payment."
                )

                # create receipt items
                # Create all receipt items directly from the order items QuerySet
                SalesReceiptItemService.create_sales_receipt_items(
                    sales_receipt=sales_receipt,
                    items=sales_order.items.all()
                )
            
                logger.info("Checkout processed successfully.")
            return CheckoutResult(
                sale=sale,
                payment=payment,
                sales_payment=sales_payment,
                receipt=sales_receipt
            )
        except Exception as e:
            logger.error(f"Error during checkout process: {e}")
            raise
