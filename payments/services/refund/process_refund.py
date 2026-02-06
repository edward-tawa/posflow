from payments.services.refund.refund_service import RefundService
from payments.services.refund.refund_payment_service import RefundPaymentService
from payments.models.refund_payment_model import RefundPayment
from payments.services.payment.payment_service import PaymentService
from transactions.services.transaction_service import TransactionService
from accounts.services.cash_account_service import CashAccountService
from accounts.services.sales_returns_account_service import SalesReturnsAccountService
from customers.models.customer_model import Customer
from payments.models.payment_model import Payment
from payments.models.refund_model import Refund
from django.db import transaction as db_transaction
from dataclasses import dataclass
from loguru import logger


@dataclass
class RefundProcessResult:
    refund: Refund
    payment: Payment
    refund_payment: RefundPayment


class RefundProcessService:
    # Service class for processing refunds

    @staticmethod
    @db_transaction.atomic
    def process_refund(*,
                       company,
                       branch,
                       payment: Payment,
                       total_amount: float,
                       reason: str,
                       customer: Customer,
                       processed_by
                       ) -> Refund:
        """
        Process a refund for a payment.

        Args:
            company: Company instance
            branch: Branch instance
            payment: Payment instance
            total_amount: float
            currency: str
            reason: str
            processed_by: User instance or identifier
        """


        # create a refund
        refund = RefundService.create_refund(
            company=company,
            branch=branch,
            payment=payment,
            total_amount=total_amount,
            currency=payment.currency,
            reason=reason,
            processed_by=processed_by
        )

        # Create payment for the refund
        payment = PaymentService.create_payment(
            company=company,
            branch=branch,
            paid_by=processed_by,
            amount=total_amount,
            payment_method=payment.payment_method,
            payment_direction="outgoing",
        )

        # create a refund payment record
        refund_payment = RefundPaymentService.create_refund_payment(
            company=company,
            branch=branch,
            refund=refund,
            payment=payment,
            payment_method=payment.payment_method,
            refunded_by=processed_by
        )

        # transaction accounts
        sales_returns_account = SalesReturnsAccountService.get_or_create_sales_returns_account(
            company=company,
            branch=branch,
            customer=customer
        )

        cash_account = CashAccountService.get_or_create_cash_account(
            company=company,
            branch=branch
        )

        # might need to adjust stock

        # create transaction
        transaction = TransactionService.create_transaction(
            company=company,
            branch=branch,
            debit_account=sales_returns_account,
            credit_account=cash_account,
            total_amount=total_amount,
            transaction_type="refund",
            transaction_category="sales_return",
            total_amount=total_amount,
            customer=customer,
        )

        TransactionService.apply_transaction_to_accounts(
            transaction=transaction,
        )

        logger.info(
            f"Refund processed | refund_id={refund.id} | payment_id={payment.id} | refund_payment_id={refund_payment.id}"
        )


        return RefundProcessResult(
            refund=refund,
            payment=payment,
            refund_payment=refund_payment
        )