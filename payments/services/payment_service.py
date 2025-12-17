from payments.models.payment_model import Payment
from django.db import transaction
from loguru import logger



class PaymentService:
    """
    Service layer for Payment domain operations.
    """

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def create_payment(**kwargs) -> Payment:
        payment = Payment.objects.create(**kwargs)
        logger.info(f"Payment created | id={payment.id}")
        return payment

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_payment(
        payment: Payment,
        **kwargs
    ) -> Payment:
        # Optional: restrict to allowed fields
        ALLOWED_UPDATE_FIELDS = {"amount", "method", "status"}
        for field, value in kwargs.items():
            if field in ALLOWED_UPDATE_FIELDS:
                setattr(payment, field, value)

        payment.save()
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

    
    @staticmethod
    @transaction.atomic
    def mark_payment_as_completed(payment: Payment) -> Payment:
        payment.status = "COMPLETED"
        payment.save(update_fields=["status"])
        logger.info(f"Payment marked as completed | id={payment.id}")
        return payment
    

    @staticmethod
    @transaction.atomic
    def mark_payment_as_failed(payment: Payment) -> Payment:
        payment.status = "FAILED"
        payment.save(update_fields=["status"])
        logger.info(f"Payment marked as failed | id={payment.id}")
        return payment
    

    @staticmethod
    @transaction.atomic
    def attach_payment_to_order(
        payment: Payment,
        order_id: int
    ) -> Payment:
        payment.order_id = order_id
        payment.save(update_fields=["order_id"])
        logger.info(f"Payment '{payment.id}' attached to Order '{order_id}'.")
        return payment
    


    @staticmethod
    @transaction.atomic
    def detach_payment_from_order(payment: Payment) -> Payment:
        payment.order = None
        payment.save(update_fields=["order"])
        logger.info(f"Payment '{payment.id}' detached from Order.")
        return payment
    

    @staticmethod
    @transaction.atomic
    def attach_payment_to_customer(
        payment: Payment,
        customer_id: int
    ) -> Payment:
        payment.customer_id = customer_id
        payment.save(update_fields=["customer_id"])
        logger.info(f"Payment '{payment.id}' attached to Customer '{customer_id}'.")
        return payment
    


    @staticmethod
    @transaction.atomic
    def detach_payment_from_customer(payment: Payment) -> Payment:
        payment.customer = None
        payment.save(update_fields=["customer"])
        logger.info(f"Payment '{payment.id}' detached from Customer.")
        return payment
    

    @staticmethod
    @transaction.atomic
    def attach_payment_to_invoice(
        payment: Payment,
        invoice_id: int
    ) -> Payment:
        payment.invoice_id = invoice_id
        payment.save(update_fields=["invoice_id"])
        logger.info(f"Payment '{payment.id}' attached to Invoice '{invoice_id}'.")
        return payment
    


    @staticmethod
    @transaction.atomic
    def detach_payment_from_invoice(payment: Payment) -> Payment:
        payment.invoice = None
        payment.save(update_fields=["invoice"])
        logger.info(f"Payment '{payment.id}' detached from Invoice.")
        return payment