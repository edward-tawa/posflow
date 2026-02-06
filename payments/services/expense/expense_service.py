from payments.models.payment_model import Payment
from payments.models.expense_model import Expense
from django.db import transaction as db_transaction
from loguru import logger
from django.core.exceptions import ObjectDoesNotExist
from users.models import User
from company.models import Company
from branch.models import Branch
from transactions.services.transaction_service import TransactionService
from accounts.services.expense_account_service import ExpenseAccountService
from accounts.services.cash_account_service import CashAccountService
from payments.services.payment.payment_service import PaymentService


class ExpenseService:
    """
    Service layer for Expense domain operations.
    Fully tailored to the Expense model.
    """

    ALLOWED_STATUSES = {"PENDING", "PAID", "UNPAID", "PARTIAL"}

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def create_expense(*,
        company: Company,
        branch: Branch,
        total_amount: float,
        total_amount_paid: float,
        category: str,
        incurred_by: User | None = None,
        description: str | None = None,
        expense_date=None
    ) -> Expense:
        """
        Creates a new expense. 'company' and 'branch' are required.
        """
        expense = Expense.objects.create(
            company=company,
            branch=branch,
            total_amount=total_amount,
            total_amount_paid=total_amount_paid,
            category=category,
            incurred_by=incurred_by,
            description=description,
            expense_date=expense_date
        )
    
        logger.info(f"Expense created | id={expense.id}")
        return expense

    # -------------------------
    # READ
    # -------------------------
    @staticmethod
    def get_expense_by_id(expense_id: int) -> Expense | None:
        try:
            return Expense.objects.get(id=expense_id)
        except ObjectDoesNotExist:
            logger.warning(f"Expense with id={expense_id} not found.")
            return None

    @staticmethod
    def list_expenses_by_status(status: str) -> list[Expense]:
        if status not in ExpenseService.ALLOWED_STATUSES:
            raise ValueError(f"Invalid status: {status}")
        return list(Expense.objects.filter(status=status))

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_expense(*,
        expense: Expense,
        total_amount: float | None = None,
        total_amount_paid: float | None = None,
        category: str | None = None,
        incurred_by: User | None = None,
        description: str | None = None,
        expense_date=None
    ) -> Expense:
        if total_amount is not None:
            expense.total_amount = total_amount
        if total_amount_paid is not None:
            expense.total_amount_paid = total_amount_paid
        if category is not None:
            expense.category = category
        if incurred_by is not None:
            expense.incurred_by = incurred_by
        if description is not None:
            expense.description = description
        if expense_date is not None:
            expense.expense_date = expense_date

        # Only save the fields that were updated
        update_fields = [f for f in ["total_amount", "total_amount_paid", "category", "incurred_by", "description", "expense_date"]
                         if getattr(expense, f) is not None]
        expense.save(update_fields=update_fields)
        logger.info(f"Expense updated | id={expense.pk}")
        return expense

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_expense(expense: Expense) -> None:
        expense_id = expense.pk
        expense.delete()
        logger.info(f"Expense deleted | id={expense_id}")

    # -------------------------
    # STATUS MANAGEMENT
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_expense_status(
        *,
        expense: Expense,
        amount_paid: float | None = None,
        status: str | None = None
    ) -> Expense:
        """
        Updates expense status.
        - If amount_paid is provided, applies payment logic and derives status.
        - If status is provided directly, performs a controlled status update.
        """

        # -------------------------
        # Apply payment-driven update
        # -------------------------
        if amount_paid is not None:
            if amount_paid <= 0:
                raise ValueError("Amount paid must be greater than zero")

            expense.total_amount_paid += amount_paid

            if expense.total_amount_paid >= expense.total_amount:
                expense.status = "PAID"
            else:
                expense.status = "PARTIAL"

            expense.save(update_fields=["total_amount_paid", "status"])

            logger.info(
                f"Expense '{expense.id}' payment applied | "
                f"amount={amount_paid} | "
                f"status={expense.status}"
            )
            return expense

        # -------------------------
        # Manual status update
        # -------------------------
        if status is not None:
            if status not in ExpenseService.ALLOWED_STATUSES:
                raise ValueError(f"Invalid status: {status}")

            expense.status = status
            expense.save(update_fields=["status"])

            logger.info(f"Expense '{expense.id}' status manually updated to '{status}'")
            return expense

        raise ValueError("Either amount_paid or status must be provided")


    @staticmethod
    @db_transaction.atomic
    def mark_expense_as_paid(expense: Expense) -> Expense:
        return ExpenseService.update_expense_status(expense, "PAID")

    @staticmethod
    @db_transaction.atomic
    def mark_expense_as_unpaid(expense: Expense) -> Expense:
        return ExpenseService.update_expense_status(expense, "UPAID")

