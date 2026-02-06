from payments.models.payment_model import Payment
from django.db import transaction
from loguru import logger
from users.models import User
from company.models import Company
from branch.models import Branch

class PaymentService:
    """
    Service layer for Payment domain operations.
    """

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def create_payment(*,
        company: Company,
        branch: Branch,
        paid_by: User | None,
        amount: float,
        payment_method: str,
        payment_direction: str = "incoming",
        reference_model: str | None = None,
        reference_id: int | None = None,
    ) -> Payment:
        payment = Payment.objects.create(
            company=company,
            branch=branch,
            paid_by=paid_by,
            total_amount=amount,
            payment_method=payment_method,
            payment_direction=payment_direction,
            reference_model=reference_model,
            reference_id=reference_id,
        )
        logger.info(f"Payment created | id={payment.id}")
        return payment

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_payment(*,
        payment: Payment,
        amount: float | None = None,
        payment_method: str | None = None,
        status: str | None = None,
    ) -> Payment:
        if amount is not None:
            payment.total_amount = amount
        if payment_method is not None:
            payment.payment_method = payment_method
        if status is not None:
            payment.status = status

        payment.save(update_fields=[f for f in ["amount", "payment_method", "status"] if getattr(payment, f) is not None])
        logger.info(f"Payment updated | id={payment.id}")
        return payment

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def delete_payment(payment: Payment) -> None:
        payment_id = payment.id
        payment.delete()
        logger.info(f"Payment deleted | id={payment_id}")

    # -------------------------
    # STATUS MANAGEMENT
    # -------------------------
    @staticmethod
    @transaction.atomic
    def mark_payment_as_completed(payment: Payment) -> Payment:
        payment.status = "completed"
        payment.save(update_fields=["status"])
        logger.info(f"Payment marked as completed | id={payment.id}")
        return payment

    @staticmethod
    @transaction.atomic
    def mark_payment_as_failed(payment: Payment) -> Payment:
        payment.status = "failed"
        payment.save(update_fields=["status"])
        logger.info(f"Payment marked as failed | id={payment.id}")
        return payment

    # -------------------------
    # RELATIONS
    # -------------------------
    @staticmethod
    @transaction.atomic
    def attach_payment_to_order(*, payment: Payment, order_id: int) -> Payment:
        payment.reference_model = "Order"
        payment.reference_id = order_id
        payment.save(update_fields=["reference_model", "reference_id"])
        logger.info(f"Payment '{payment.id}' attached to Order '{order_id}'.")
        return payment

    @staticmethod
    @transaction.atomic
    def detach_payment_from_order(payment: Payment) -> Payment:
        payment.reference_model = None
        payment.reference_id = None
        payment.save(update_fields=["reference_model", "reference_id"])
        logger.info(f"Payment '{payment.id}' detached from Order.")
        return payment

    @staticmethod
    @transaction.atomic
    def attach_payment_to_customer(*, payment: Payment, customer_id: int) -> Payment:
        payment.reference_model = "Customer"
        payment.reference_id = customer_id
        payment.save(update_fields=["reference_model", "reference_id"])
        logger.info(f"Payment '{payment.id}' attached to Customer '{customer_id}'.")
        return payment

    @staticmethod
    @transaction.atomic
    def detach_payment_from_customer(payment: Payment) -> Payment:
        payment.reference_model = None
        payment.reference_id = None
        payment.save(update_fields=["reference_model", "reference_id"])
        logger.info(f"Payment '{payment.id}' detached from Customer.")
        return payment

    @staticmethod
    @transaction.atomic
    def attach_payment_to_invoice(*, payment: Payment, invoice_id: int) -> Payment:
        payment.reference_model = "Invoice"
        payment.reference_id = invoice_id
        payment.save(update_fields=["reference_model", "reference_id"])
        logger.info(f"Payment '{payment.id}' attached to Invoice '{invoice_id}'.")
        return payment

    @staticmethod
    @transaction.atomic
    def detach_payment_from_invoice(payment: Payment) -> Payment:
        payment.reference_model = None
        payment.reference_id = None
        payment.save(update_fields=["reference_model", "reference_id"])
        logger.info(f"Payment '{payment.id}' detached from Invoice.")
        return payment
