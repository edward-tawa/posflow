from payments.models.payment_receipt_model import PaymentReceipt
from django.db import transaction
from loguru import logger


class PaymentReceiptService:
    """
    Service layer for PaymentReceipt domain operations.
    Handles CRUD, status updates, and relations.
    """

    ALLOWED_UPDATE_FIELDS = {"amount", "receipt_date", "issued_by"}
    ALLOWED_STATUSES = {"DRAFT", "SENT", "CANCELLED", "PAID"}
    RELATION_FIELDS = {"payment", "customer", "order"}

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def create_payment_receipt(**kwargs) -> PaymentReceipt:
        receipt = PaymentReceipt.objects.create(**kwargs)
        logger.info(f"PaymentReceipt created | id={receipt.id}")
        return receipt

    # -------------------------
    # READ
    # -------------------------
    @staticmethod
    def get_receipt_by_id(receipt_id: int) -> PaymentReceipt | None:
        try:
            return PaymentReceipt.objects.get(id=receipt_id)
        except PaymentReceipt.DoesNotExist:
            logger.warning(f"PaymentReceipt with id {receipt_id} not found.")
            return None

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_payment_receipt(receipt: PaymentReceipt, **kwargs) -> PaymentReceipt:
        for field, value in kwargs.items():
            if field not in PaymentReceiptService.ALLOWED_UPDATE_FIELDS:
                raise ValueError(f"Field '{field}' cannot be updated")
            setattr(receipt, field, value)

        receipt.save()
        logger.info(f"PaymentReceipt updated | id={receipt.id}")
        return receipt

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def delete_payment_receipt(receipt: PaymentReceipt) -> None:
        receipt_id = receipt.id
        receipt.delete()
        logger.info(f"PaymentReceipt deleted | id={receipt_id}")

    # -------------------------
    # STATUS MANAGEMENT
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_payment_receipt_status(
        receipt: PaymentReceipt,
        new_status: str
    ) -> PaymentReceipt:
        if new_status not in PaymentReceiptService.ALLOWED_STATUSES:
            logger.error(
                f"Invalid status '{new_status}' for PaymentReceipt '{receipt.id}'."
            )
            raise ValueError(f"Invalid status: {new_status}")

        receipt.status = new_status
        receipt.save(update_fields=["status"])
        logger.info(
            f"PaymentReceipt '{receipt.id}' status updated to '{new_status}'."
        )
        return receipt

    @staticmethod
    @transaction.atomic
    def mark_receipt_as_sent(receipt: PaymentReceipt) -> PaymentReceipt:
        return PaymentReceiptService.update_payment_receipt_status(receipt, "SENT")

    @staticmethod
    @transaction.atomic
    def mark_receipt_as_cancelled(receipt: PaymentReceipt) -> PaymentReceipt:
        return PaymentReceiptService.update_payment_receipt_status(receipt, "CANCELLED")

    # -------------------------
    # RELATION MANAGEMENT
    # -------------------------
    @staticmethod
    @transaction.atomic
    def attach_relation(
        receipt: PaymentReceipt,
        relation_field: str,
        entity_id: int
    ) -> PaymentReceipt:
        if relation_field not in PaymentReceiptService.RELATION_FIELDS:
            raise ValueError(f"Invalid relation field: {relation_field}")

        setattr(receipt, f"{relation_field}_id", entity_id)
        receipt.save(update_fields=[f"{relation_field}_id"])
        logger.info(
            f"PaymentReceipt '{receipt.id}' attached to {relation_field.capitalize()} '{entity_id}'."
        )
        return receipt

    @staticmethod
    @transaction.atomic
    def detach_relation(
        receipt: PaymentReceipt,
        relation_field: str
    ) -> PaymentReceipt:
        if relation_field not in PaymentReceiptService.RELATION_FIELDS:
            raise ValueError(f"Invalid relation field: {relation_field}")

        setattr(receipt, relation_field, None)
        receipt.save(update_fields=[relation_field])
        logger.info(
            f"PaymentReceipt '{receipt.id}' detached from {relation_field.capitalize()}."
        )
        return receipt
