from suppliers.models.purchase_payment_model import PurchasePayment
from suppliers.models.supplier_model import Supplier
from loguru import logger
from django.db import transaction as db_transaction


class PurchasePaymentService:
    """
    Service class for managing purchase payments.
    Provides methods for creating, updating, deleting payments,
    attaching/detaching them to/from suppliers,
    and status management with business rules enforced.
    """

    ALLOWED_STATUSES = {"DRAFT", "COMPLETED", "CANCELLED"}
    ALLOWED_UPDATE_FIELDS = {"amount", "payment_date", "payment_method", "notes"}

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def create_payment(**kwargs) -> PurchasePayment:
        amount = kwargs.get("amount", 0.0)
        if amount < 0:
            raise ValueError("Amount must be non-negative")

        # Validate initial status
        status = kwargs.get("status", "DRAFT")
        if status not in PurchasePaymentService.ALLOWED_STATUSES:
            raise ValueError(f"Invalid status: {status}")
        kwargs["status"] = status

        payment = PurchasePayment.objects.create(**kwargs)
        logger.info(
            f"Purchase Payment '{payment.id}' created for supplier "
            f"'{payment.supplier.name if payment.supplier else 'None'}' with status '{payment.status}'."
        )
        return payment

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_payment(payment: PurchasePayment, **kwargs) -> PurchasePayment:
        for key, value in kwargs.items():
            if key not in PurchasePaymentService.ALLOWED_UPDATE_FIELDS:
                logger.warning(f"Ignored invalid update field '{key}' for payment '{payment.id}'")
                continue

            if key == "amount" and value < 0:
                raise ValueError("Amount must be non-negative")

            setattr(payment, key, value)

        payment.save()
        logger.info(
            f"Purchase Payment '{payment.id}' updated for supplier "
            f"'{payment.supplier.name if payment.supplier else 'None'}'."
        )
        return payment

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_payment(payment: PurchasePayment) -> None:
        payment_id = payment.id
        payment.delete()
        logger.info(f"Purchase Payment '{payment_id}' deleted.")

    # -------------------------
    # RELATION MANAGEMENT
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def attach_to_supplier(payment: PurchasePayment, supplier: Supplier) -> PurchasePayment:
        previous_supplier = payment.supplier
        payment.supplier = supplier
        payment.save(update_fields=['supplier'])
        logger.info(
            f"Purchase Payment '{payment.id}' attached to supplier '{supplier.id}' "
            f"(previous supplier: '{previous_supplier.id if previous_supplier else 'None'}')."
        )
        return payment

    @staticmethod
    @db_transaction.atomic
    def detach_from_supplier(payment: PurchasePayment) -> PurchasePayment:
        previous_supplier = payment.supplier
        payment.supplier = None
        payment.save(update_fields=['supplier'])
        logger.info(
            f"Purchase Payment '{payment.id}' detached from supplier "
            f"'{previous_supplier.id if previous_supplier else 'None'}'."
        )
        return payment

    # -------------------------
    # STATUS MANAGEMENT
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_payment_status(payment: PurchasePayment, new_status: str) -> PurchasePayment:
        if new_status not in PurchasePaymentService.ALLOWED_STATUSES:
            logger.error(
                f"Attempted to set invalid status '{new_status}' for payment '{payment.id}'"
            )
            raise ValueError(f"Invalid status: {new_status}")

        payment.status = new_status
        payment.save(update_fields=['status'])
        logger.info(f"Purchase Payment '{payment.id}' status updated to '{new_status}'.")
        return payment

    # -------------------------
    # NOTES MANAGEMENT
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_payment_notes(payment: PurchasePayment, new_notes: str) -> PurchasePayment:
        payment.notes = new_notes
        payment.save(update_fields=['notes'])
        logger.info(f"Purchase Payment '{payment.id}' notes updated.")
        return payment

    # -------------------------
    # BULK OPERATIONS (Optional)
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def bulk_update_status(payments: list[PurchasePayment], new_status: str) -> None:
        if new_status not in PurchasePaymentService.ALLOWED_STATUSES:
            raise ValueError(f"Invalid status: {new_status}")

        for payment in payments:
            payment.status = new_status
        PurchasePayment.objects.bulk_update(payments, ['status'])
        logger.info(f"Bulk updated status to '{new_status}' for {len(payments)} payments.")
