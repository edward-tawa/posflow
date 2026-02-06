from payments.models.payment_model import Payment
from payments.models.purchase_payment_model import PurchasePayment
from payments.models.payment_method_model import PaymentMethod
from payments.models.refund_payment_model import RefundPayment
from payments.models.payment_method_model import PaymentMethod
from django.db import transaction as db_transaction
from loguru import logger
from django.core.exceptions import ObjectDoesNotExist
from payments.models.expense_model import Expense
from users.models import User
from company.models import Company
from branch.models import Branch
from typing import Union



class RefundPaymentService:
    # Refund payment service class

    @staticmethod
    @db_transaction
    def create_refund_payment(*,
                                company: Company,
                                branch: Branch,
                                refund: RefundPayment,
                                payment: Payment,
                                payment_method: PaymentMethod,
                                refunded_by: User
                                ) -> RefundPayment:
        """
        Create a refund payment record.
        """

        try:
            refund_payment = RefundPayment.objects.create(
                company=company,
                branch=branch,
                refund=refund,
                payment=payment,
                payment_method=payment_method,
                paid_by=refunded_by
            )
            logger.info(f"Created RefundPayment ID: {refund_payment.id}")
            return refund_payment
        except Exception as e:
            logger.error(f"Error creating RefundPayment: {e}")
            raise

    
    @staticmethod
    def get_refund_payment(*,
                             company: Company,
                             branch: Branch,
                             refund: RefundPayment,
                             payment: Payment
                             ) -> Union[RefundPayment, None]:
        """
        Retrieve a refund payment record.
        """

        try:
            refund_payment = RefundPayment.objects.get(
                company=company,
                branch=branch,
                refund=refund,
                payment=payment
            )
            return refund_payment
        except ObjectDoesNotExist:
            logger.warning("RefundPayment not found.")
            return None
        

    @staticmethod
    @db_transaction
    def update_refund_payment(*,
                               company: Company,
                               branch: Branch,
                               refund: RefundPayment,
                               payment: Payment,
                               payment_method: PaymentMethod,
                               refunded_by: User
                               ) -> RefundPayment:
        """
        Update a refund payment record.
        """
        updated_fields = {
            'refund': refund,
            'payment_method': payment_method,
            'paid_by': refunded_by
        }

        try:
            refund_payment = RefundPayment.objects.get(
                company=company,
                branch=branch,
                payment=payment
            )
            for field, value in updated_fields.items():
                setattr(refund_payment, field, value)
            refund_payment.save()
            logger.info(f"Updated RefundPayment ID: {refund_payment.id}")
            return refund_payment
        except ObjectDoesNotExist:
            logger.error("RefundPayment to update not found.")
            raise

    

    @staticmethod
    @db_transaction
    def add_refund_payment_to_payment(
            refund_payment: RefundPayment,
            payment: Payment
    ) -> RefundPayment:
        """
        Attach a refund payment to a payment.
        """

        try:
            refund_payment.payment = payment
            refund_payment.save(update_fields=['payment'])
            logger.info(f"Attached RefundPayment ID: {refund_payment.id} to Payment ID: {payment.id}")
            return refund_payment
        except Exception as e:
            logger.error(f"Error attaching RefundPayment to Payment: {e}")
            raise

    

    @staticmethod
    @db_transaction
    def remove_refund_payment_from_payment(
            refund_payment: RefundPayment
    ) -> RefundPayment:
        """
        Detach a refund payment from its payment.
        """

        try:
            refund_payment.payment = None
            refund_payment.save(update_fields=['payment'])
            logger.info(f"Detached RefundPayment ID: {refund_payment.id} from its Payment")
            return refund_payment
        except Exception as e:
            logger.error(f"Error detaching RefundPayment from Payment: {e}")
            raise