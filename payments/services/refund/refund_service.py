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
    def create_refund(*,
        company,
        branch,
        payment,
        total_amount: float,
        currency=None,
        reason: str = "customer_request",
        processed_by=None,
        notes: str | None = None
    ) -> Refund:
        refund = Refund.objects.create(
            company=company,
            branch=branch,
            payment=payment,
            total_amount=total_amount,
            currency=currency,
            reason=reason,
            processed_by=processed_by,
            notes=notes
        )
        logger.info(f"Refund created | id={refund.id}")
        return refund

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_refund(
        refund: Refund,
        amount: float | None = None,
        reason: str | None = None,
        status: str | None = None,
        notes: str | None = None,
    ) -> Refund:

        if amount is not None:
            refund.total_amount = amount
        if reason is not None:
            refund.reason = reason
        if status is not None:
            refund.status = status
        if notes is not None:
            refund.notes = notes

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

    # -------------------------
    # STATUS MANAGEMENT
    # -------------------------
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

    @staticmethod
    @transaction.atomic
    def cancel_refund(refund: Refund) -> Refund:
        refund.status = "CANCELLED"
        refund.save(update_fields=["status"])
        logger.info(f"Refund marked as cancelled | id={refund.id}")
        return refund

    @staticmethod
    @transaction.atomic
    def update_refund_status(refund: Refund, new_status: str) -> Refund:
        ALLOWED_STATUSES = {"PENDING", "PROCESSED", "FAILED", "CANCELLED"}
        if new_status not in ALLOWED_STATUSES:
            logger.error(f"Invalid status '{new_status}' for refund '{refund.id}'")
            raise ValueError(f"Invalid status: {new_status}")

        refund.status = new_status
        refund.save(update_fields=['status'])
        logger.info(f"Refund '{refund.id}' status updated to '{new_status}'")
        return refund

    # -------------------------
    # RELATION MANAGEMENT
    # -------------------------
    @staticmethod
    @transaction.atomic
    def attach_to_payment(refund: Refund, payment_id: int) -> Refund:
        refund.payment_id = payment_id
        refund.save(update_fields=['payment_id'])
        logger.info(f"Refund '{refund.id}' attached to Payment '{payment_id}'.")
        return refund

    @staticmethod
    @transaction.atomic
    def detach_from_payment(refund: Refund) -> Refund:
        refund.payment = None
        refund.save(update_fields=['payment'])
        logger.info(f"Refund '{refund.id}' detached from Payment.")
        return refund
