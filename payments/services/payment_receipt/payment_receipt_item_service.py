from payments.models.payment_receipt_item_model import PaymentReceiptItem
from django.db import transaction
from loguru import logger


class PaymentReceiptItemService:
    """
    Service layer for PaymentReceiptItem domain operations.
    Handles CRUD, relations, and refund state.
    """

    ALLOWED_UPDATE_FIELDS = {"description", "quantity", "unit_price", "total"}
    
    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def create_payment_receipt_item(**kwargs) -> PaymentReceiptItem:
        item = PaymentReceiptItem.objects.create(**kwargs)
        logger.info(f"PaymentReceiptItem created | id={item.id}")
        return item

    # -------------------------
    # READ
    # -------------------------
    @staticmethod
    def get_item_by_id(item_id: int) -> PaymentReceiptItem | None:
        try:
            return PaymentReceiptItem.objects.get(id=item_id)
        except PaymentReceiptItem.DoesNotExist:
            logger.warning(f"PaymentReceiptItem with id {item_id} not found.")
            return None

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def update_payment_receipt_item(
        item: PaymentReceiptItem,
        **kwargs
    ) -> PaymentReceiptItem:
        for field, value in kwargs.items():
            if field not in PaymentReceiptItemService.ALLOWED_UPDATE_FIELDS:
                raise ValueError(f"Field '{field}' cannot be updated")
            setattr(item, field, value)

        item.save()
        logger.info(f"PaymentReceiptItem updated | id={item.id}")
        return item

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def delete_payment_receipt_item(item: PaymentReceiptItem) -> None:
        item_id = item.id
        item.delete()
        logger.info(f"PaymentReceiptItem deleted | id={item_id}")

    # -------------------------
    # RELATION MANAGEMENT
    # -------------------------
    @staticmethod
    @transaction.atomic
    def attach_to_payment_receipt(
        item: PaymentReceiptItem,
        receipt_id: int
    ) -> PaymentReceiptItem:
        item.payment_receipt_id = receipt_id
        item.save(update_fields=["payment_receipt_id"])
        logger.info(
            f"PaymentReceiptItem '{item.id}' attached to PaymentReceipt '{receipt_id}'."
        )
        return item

    @staticmethod
    @transaction.atomic
    def detach_from_payment_receipt(item: PaymentReceiptItem) -> PaymentReceiptItem:
        item.payment_receipt = None
        item.save(update_fields=["payment_receipt"])
        logger.info(
            f"PaymentReceiptItem '{item.id}' detached from PaymentReceipt."
        )
        return item

    # -------------------------
    # REFUND STATE
    # -------------------------
    @staticmethod
    @transaction.atomic
    def mark_item_as_refunded(item: PaymentReceiptItem) -> PaymentReceiptItem:
        item.is_refunded = True
        item.save(update_fields=["is_refunded"])
        logger.info(
            f"PaymentReceiptItem '{item.id}' marked as refunded."
        )
        return item

    @staticmethod
    @transaction.atomic
    def unmark_item_as_refunded(item: PaymentReceiptItem) -> PaymentReceiptItem:
        item.is_refunded = False
        item.save(update_fields=["is_refunded"])
        logger.info(
            f"PaymentReceiptItem '{item.id}' unmarked as refunded."
        )
        return item
