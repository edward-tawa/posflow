from payments.services.payment.payment_service import PaymentService
from accounts.services.cash_account_service import CashAccountService
from accounts.services.expense_account_service import ExpenseAccountService
from payments.services.expense.expense_payment_service import ExpensePaymentService
from payments.services.expense.expense_service import ExpenseService
from transactions.services.transaction_service import TransactionService
from payments.models.expense_model import Expense
from payments.models.expense_payment_model import ExpensePayment
from django.db import transaction as db_transaction
from loguru import logger

# Use this one for production.

class ProcessExpensePaymentService:
    """Service class to process expense payments."""

    @staticmethod
    @db_transaction.atomic
    def process_expense_payment(*,
                                company,
                                branch,
                                expense: Expense,
                                payment_method,
                                total_amount: float,
                                paid_by
                                ) -> ExpensePayment:
        """
        Process payment for an expense.

        Args:
            company: Company instance
            branch: Branch instance
            expense: Expense instance
            payment_method: str
            amount: float
            paid_by: User instance or identifier

        Returns:
            ExpensePayment instance
        """

        try:
            # -------------------
            # Input validation
            # -------------------

            expense = (
                Expense.objects.select_for_update().get(id=expense.pk)
            )
            if total_amount <= 0:
                raise ValueError("Payment amount must be greater than zero")

            if expense.company != company or expense.branch != branch:
                raise ValueError("Expense does not belong to the given company or branch")

            remaining_amount = expense.total_amount - expense.total_amount_paid

            if total_amount > remaining_amount:
                raise ValueError(f"Payment amount exceeds remaining expense balance ({remaining_amount})")

            # -------------------
            # Create Payment record
            # -------------------
            payment = PaymentService.create_payment(
                company=company,
                branch=branch,
                amount=total_amount,
                payment_method=payment_method,
                payment_direction='outgoing',
                paid_by=paid_by
            )

            # -------------------
            # Create ExpensePayment record
            # -------------------
            expense_payment = ExpensePaymentService.create_expense_payment(
                company=company,
                branch=branch,
                expense=expense,
                payment=payment,
                payment_method=payment_method,
                paid_by=paid_by
            )

            # --------------------
            # Update expense status
            # ---------------------
            ExpenseService.update_expense_status(
                expense=expense,
                amount_paid=total_amount
            )

            # Transaction accounts
            cash_account = CashAccountService.get_cash_accounts_by_company(company=company).first()

            expense_account = ExpenseAccountService.get_expense_accounts_by_company(company=company).first()

            if not cash_account or not expense_account:
                raise ValueError("Required accounts (cash or expense) are not properly configured.")
            
            # Record the transaction
            transaction = TransactionService.create_transaction(
                company=company,
                branch=branch,
                amount=total_amount,
                debit_account=expense_account,
                credit_account=cash_account,
                transaction_type="expense_payment",
                transaction_category="expense",
                total_amount=total_amount,
            )

            # Apply transaction to expense
            TransactionService.apply_transaction_to_accounts(
                transaction=transaction,
            )


            logger.info(
                f"Processed payment for Expense ID: {expense.id} | Payment ID: {payment.id} | Amount: {total_amount}"
            )

            return expense_payment

        except Exception as e:
            logger.error(f"Failed to process payment for Expense ID: {getattr(expense, 'id', 'Unknown')} | Error: {str(e)}")
            raise
