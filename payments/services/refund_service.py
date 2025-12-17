from payments.models.refund_model import Refund
from django.db import transaction
from loguru import logger



class RefundService:
    """
    Service layer for Refund domain operations.
    """

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def create_refund(**kwargs) -> Refund:
        refund = Refund.objects.create(**kwargs)
        logger.info(f"Refund created | id={refund.id}")
        return refund

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_refund(
        refund: Refund,
        **kwargs
    ) -> Refund:
        # Optional: restrict to allowed fields
        ALLOWED_UPDATE_FIELDS = {"amount", "reason", "status"}
        for field, value in kwargs.items():
            if field in ALLOWED_UPDATE_FIELDS:
                setattr(refund, field, value)

        refund.save()
        logger.info(f"Refund updated | id={refund.id}")
        return refund

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def delete_refund(refund: Refund) -> None:
        refund_id = refund.id
        refund.delete()
        logger.info(f"Refund deleted | id={refund_id}")

    

    @staticmethod
    @transaction.atomic
    def mark_refund_as_processed(refund: Refund) -> Refund:
        refund.status = "PROCESSED"
        refund.save(update_fields=["status"])
        logger.info(f"Refund marked as processed | id={refund.id}")
        return refund
    

    @staticmethod
    @transaction.atomic
    def mark_refund_as_failed(refund: Refund) -> Refund:
        refund.status = "FAILED"
        refund.save(update_fields=["status"])
        logger.info(f"Refund marked as failed | id={refund.id}")
        return refund
    

    @staticmethod
    @transaction.atomic
    def mark_refund_as_pending(refund: Refund) -> Refund:
        refund.status = "PENDING"
        refund.save(update_fields=["status"])
        logger.info(f"Refund marked as pending | id={refund.id}")
        return refund
    

    # -------------------------
    # RELATION MANAGEMENT
    # -------------------------
    @staticmethod
    @transaction.atomic
    def attach_to_payment(
        refund: Refund,
        payment_id: int
    ) -> Refund:
        refund.payment_id = payment_id
        refund.save(update_fields=['payment_id'])
        logger.info(
            f"Refund '{refund.id}' attached to Payment '{payment_id}'."
        )
        return refund
    

    @staticmethod
    @transaction.atomic
    def detach_from_payment(refund: Refund) -> Refund:
        refund.payment = None
        refund.save(update_fields=['payment'])
        logger.info(f"Refund '{refund.id}' detached from Payment.")
        return refund
    

    @staticmethod
    @transaction.atomic
    def attach_to_order(
        refund: Refund,
        order_id: int
    ) -> Refund:
        refund.order_id = order_id
        refund.save(update_fields=['order_id'])
        logger.info(
            f"Refund '{refund.id}' attached to Order '{order_id}'."
        )
        return refund
    

    @staticmethod
    @transaction.atomic
    def detach_from_order(refund: Refund) -> Refund:
        refund.order = None
        refund.save(update_fields=['order'])
        logger.info(f"Refund '{refund.id}' detached from Order.")
        return refund
    

    @staticmethod
    @transaction.atomic
    def attach_refund_to_customer(
        refund: Refund,
        customer_id: int
    ) -> Refund:
        refund.customer_id = customer_id
        refund.save(update_fields=['customer_id'])
        logger.info(
            f"Refund '{refund.id}' attached to Customer '{customer_id}'."
        )
        return refund
    

    @staticmethod
    @transaction.atomic
    def detach_refund_from_customer(refund: Refund) -> Refund:
        refund.customer = None
        refund.save(update_fields=['customer'])
        logger.info(f"Refund '{refund.id}' detached from Customer.")
        return refund
    

    # -------------------------
    # STATUS MANAGEMENT
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_refund_status(
        refund: Refund,
        new_status: str
    ) -> Refund:
        ALLOWED_STATUSES = {"PENDING", "PROCESSED", "FAILED", "CANCELLED"}

        if new_status not in ALLOWED_STATUSES:
            logger.error(
                f"Attempted to set invalid status '{new_status}' for refund '{refund.id}'."
            )
            raise ValueError(f"Invalid status: {new_status}")

        refund.status = new_status
        refund.save(update_fields=['status'])
        logger.info(
            f"Refund '{refund.id}' status updated to '{new_status}'."
        )
        return refund
    
    @staticmethod
    @transaction.atomic
    def cancel_refund(refund: Refund) -> Refund:
        refund.status = "CANCELLED"
        refund.save(update_fields=["status"])
        logger.info(f"Refund marked as cancelled | id={refund.id}")
        return refund