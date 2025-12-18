from payments.models.payment_model import Payment
from payments.models.expense_model import Expense
from django.db import transaction as db_transaction
from loguru import logger
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status


class ExpenseService:
    """
    Service layer for Expense domain operations.
    Fully tailored to the Expense model.
    """

    ALLOWED_UPDATE_FIELDS = {"amount", "description", "expense_date", "category", "incurred_by"}
    ALLOWED_STATUSES = {"PENDING", "PAID", "UPAID"}

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def create_expense(**kwargs) -> Expense:
        """
        Create a new expense. 'company' and 'branch' are required.
        """
        if "company" not in kwargs or "branch" not in kwargs:
            raise ValueError("'company' and 'branch' are required fields.")

        expense = Expense.objects.create(**kwargs)
        logger.info(f"Expense created | id={expense.id} | number={expense.expense_number}")
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
    def update_expense(expense: Expense, **kwargs) -> Expense:
        for key in kwargs:
            if key not in ExpenseService.ALLOWED_UPDATE_FIELDS:
                raise ValueError(f"Field '{key}' cannot be updated.")

        for key, value in kwargs.items():
            setattr(expense, key, value)

        expense.save(update_fields=list(kwargs.keys()))
        logger.info(f"Expense updated | id={expense.id}")
        return expense

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_expense(expense: Expense) -> None:
        expense_id = expense.id
        expense.delete()
        logger.info(f"Expense deleted | id={expense_id}")

    # -------------------------
    # STATUS MANAGEMENT
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_expense_status(expense: Expense, status: str) -> Expense:
        if status not in ExpenseService.ALLOWED_STATUSES:
            raise ValueError(f"Invalid status: {status}")

        expense.status = status
        expense.save(update_fields=["status"])
        logger.info(f"Expense '{expense.id}' status updated to '{status}'")
        return expense

    @staticmethod
    @db_transaction.atomic
    def mark_expense_as_paid(expense: Expense) -> Expense:
        return ExpenseService.update_expense_status(expense, "PAID")

    @staticmethod
    @db_transaction.atomic
    def mark_expense_as_unpaid(expense: Expense) -> Expense:
        return ExpenseService.update_expense_status(expense, "UPAID")

    # -------------------------
    # PAYMENT RELATIONS
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def attach_expense_to_payment(expense: Expense, payment_id: int) -> Expense:
        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            logger.error(f"Payment with id={payment_id} does not exist.")
            raise

        expense.payment = payment
        expense.save(update_fields=["payment"])
        logger.info(f"Expense '{expense.id}' attached to Payment '{payment.id}'")
        return expense

    @staticmethod
    @db_transaction.atomic
    def detach_expense_from_payment(expense: Expense) -> Expense:
        expense.payment = None
        expense.save(update_fields=["payment"])
        logger.info(f"Expense '{expense.id}' detached from Payment")
        return expense
    

    @action(detail=True, methods=['post'], url_path='mark-paid')
    def mark_paid(self, request, pk=None):
        expense = self.get_object()
        ExpenseService.mark_expense_as_paid(expense)
        return Response({"status": "PAID"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='mark-unpaid')
    def mark_unpaid(self, request, pk=None):
        expense = self.get_object()
        ExpenseService.mark_expense_as_unpaid(expense)
        return Response({"status": "UPAID"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='update-status')
    def update_status(self, request, pk=None):
        expense = self.get_object()
        new_status = request.data.get("status")
        ExpenseService.update_expense_status(expense, new_status)
        return Response({"status": new_status}, status=status.HTTP_200_OK)

    # -------------------------
    # PAYMENT RELATION ACTIONS
    # -------------------------
    @action(detail=True, methods=['post'], url_path='attach-payment')
    def attach_payment(self, request, pk=None):
        expense = self.get_object()
        payment_id = request.data.get("payment_id")
        ExpenseService.attach_expense_to_payment(expense, payment_id)
        return Response({"payment_id": payment_id}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='detach-payment')
    def detach_payment(self, request, pk=None):
        expense = self.get_object()
        ExpenseService.detach_expense_from_payment(expense)
        return Response({"payment_detached": True}, status=status.HTTP_200_OK)
