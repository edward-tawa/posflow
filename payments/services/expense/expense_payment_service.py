from payments.models.payment_model import Payment
from payments.models.purchase_payment_model import PurchasePayment
from payments.models.payment_method_model import PaymentMethod
from django.db import transaction as db_transaction
from loguru import logger
from django.core.exceptions import ObjectDoesNotExist
from suppliers.models.purchase_invoice_model import PurchaseInvoice
from suppliers.models.purchase_order_model import PurchaseOrder
from payments.models.expense_payment_model import ExpensePayment
from payments.models.expense_model import Expense
from users.models import User
from company.models import Company
from branch.models import Branch
from typing import Union



class ExpensePaymentService:
    # Expense payment service class

    @staticmethod
    @db_transaction
    def create_expense_payment(*,
                                company: Company,
                                branch: Branch,
                                expense: Expense,
                                payment: Payment,
                                payment_method: PaymentMethod,
                                paid_by: User
                                ) -> ExpensePayment:
        """
        Create an expense payment record.
        """

        try:
            expense_payment = ExpensePayment.objects.create(
                company=company,
                branch=branch,
                expense=expense,
                payment=payment,
                payment_method=payment_method,
                paid_by=paid_by
            )

            logger.info(f"Created ExpensePayment ID: {expense_payment.id}")

            # link expense payment to payment
            ExpensePaymentService.add_expense_payment_to_payment(
                expense_payment=expense_payment,
                payment=payment
            )

            # link expense payment to expense
            ExpensePaymentService.add_expense_payment_to_expense(
                expense_payment=expense_payment,
                expense=expense
            )
            
            return expense_payment
        except Exception as e:
            logger.error(f"Error creating ExpensePayment: {e}")
            raise

    
    @staticmethod
    def get_expense_payment(*,
                             company: Company,
                             branch: Branch,
                             expense: Expense,
                             payment: Payment
                             ) -> Union[ExpensePayment, None]:
        """
        Retrieve an expense payment record.
        """

        try:
            expense_payment = ExpensePayment.objects.get(
                company=company,
                branch=branch,
                expense=expense,
                payment=payment
            )
            logger.info(f"Retrieved ExpensePayment ID: {expense_payment.id}")
            return expense_payment
        except ObjectDoesNotExist:
            logger.warning("ExpensePayment not found.")
            return None
        

    @staticmethod
    @db_transaction
    def update_expense_payment(
            company: Company,
            branch: Branch,
            expense: Expense,
            payment: Payment,
            payment_method: PaymentMethod,
            paid_by: User
    ) -> ExpensePayment:
        """
        Update an expense payment record.
        """
        updated_fields = {
            'expense': expense,
            'payment_method': payment_method,
            'paid_by': paid_by
        }

        try:
            expense_payment = ExpensePayment.objects.get(
                company=company,
                branch=branch,
                payment=payment
            )
            for field, value in updated_fields.items():
                setattr(expense_payment, field, value)
            expense_payment.save()
            logger.info(f"Updated ExpensePayment ID: {expense_payment.id}")
            return expense_payment
        except ObjectDoesNotExist:
            logger.error("ExpensePayment to update not found.")
            raise

    

    @staticmethod
    @db_transaction
    def add_expense_payment_to_payment(
            expense_payment: ExpensePayment,
            payment: Payment
    ) -> ExpensePayment:
        """
        Attach an expense payment to a payment record.
        """
        try:
            expense_payment.payment = payment
            expense_payment.save(update_fields=['payment'])
            logger.info(f"Attached ExpensePayment ID: {expense_payment.id} to Payment ID: {payment.id}")
            return expense_payment
        except Exception as e:
            logger.error(f"Error attaching ExpensePayment to Payment: {e}")
            raise

    
    @staticmethod
    @db_transaction
    def remove_expense_payment_from_payment(
            expense_payment: ExpensePayment
    ) -> ExpensePayment:
        """
        Detach an expense payment from its payment record.
        """
        try:
            expense_payment.payment = None
            expense_payment.save(update_fields=['payment'])
            logger.info(f"Detached ExpensePayment ID: {expense_payment.id} from its Payment")
            return expense_payment
        except Exception as e:
            logger.error(f"Error detaching ExpensePayment from Payment: {e}")
            raise

    
    @staticmethod
    @db_transaction
    def add_expense_payment_to_expense(
            expense_payment: ExpensePayment,
            expense: Expense
    ) -> ExpensePayment:
        """
        Attach an expense payment to an expense record.
        """
        try:
            expense_payment.expense = expense
            expense_payment.save(update_fields=['expense'])
            logger.info(f"Attached ExpensePayment ID: {expense_payment.id} to Expense ID: {expense.id}")
            return expense_payment
        except Exception as e:
            logger.error(f"Error attaching ExpensePayment to Expense: {e}")
            raise
    
    @staticmethod
    @db_transaction
    def remove_expense_payment_from_expense(
            expense_payment: ExpensePayment
    ) -> ExpensePayment:
        """
        Detach an expense payment from its expense record.
        """
        try:
            expense_payment.expense = None
            expense_payment.save(update_fields=['expense'])
            logger.info(f"Detached ExpensePayment ID: {expense_payment.id} from its Expense")
            return expense_payment
        except Exception as e:
            logger.error(f"Error detaching ExpensePayment from Expense: {e}")
            raise