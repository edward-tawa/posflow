from payments.models.payment_allocation_model import PaymentAllocation
from django.db import transaction as db_transaction
from loguru import logger
from django.core.exceptions import ObjectDoesNotExist, ValidationError


class PaymentAllocationService:
    """
    Service layer for PaymentAllocation domain operations.
    Handles creation, application, reversal, deletion, and relation management
    with strict validation and audit logging.
    """

    ALLOWED_STATUSES = {"PENDING", "APPLIED", "REVERSED"}

    # Allowed state transitions
    ALLOWED_TRANSITIONS = {
        "PENDING": {"APPLIED", "CANCELLED"},
        "APPLIED": {"REVERSED"},
        "REVERSED": set(),
    }

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def create_payment_allocation(*, payment, invoice, amount) -> PaymentAllocation:
        if amount <= 0:
            raise ValueError("Allocation amount must be greater than zero.")

        if invoice.is_paid:
            raise ValueError("Cannot allocate payment to a fully paid invoice.")

        if amount > getattr(payment, "remaining_amount", amount):
            raise ValueError("Allocation exceeds remaining payment amount.")

        if amount > getattr(invoice, "outstanding_balance", amount):
            raise ValueError("Allocation exceeds invoice balance.")

        allocation = PaymentAllocation.objects.create(
            payment=payment,
            invoice=invoice,
            amount=amount,
            status="PENDING",
        )

        logger.info(f"PaymentAllocation created | id={allocation.id} | amount={amount}")
        return allocation

    # -------------------------
    # APPLY
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def apply_allocation(allocation: PaymentAllocation) -> PaymentAllocation:
        if allocation.status != "PENDING":
            raise ValueError(f"Allocation cannot be applied from status '{allocation.status}'.")

        allocation.status = "APPLIED"
        allocation.save(update_fields=["status"])

        logger.info(f"PaymentAllocation applied | id={allocation.id}")
        return allocation

    # -------------------------
    # REVERSE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def reverse_allocation(allocation: PaymentAllocation, *, reason: str | None = None) -> PaymentAllocation:
        if allocation.status != "APPLIED":
            raise ValueError("Only applied allocations can be reversed.")

        allocation.status = "REVERSED"
        allocation.save(update_fields=["status"])

        logger.warning(f"PaymentAllocation reversed | id={allocation.id} | reason={reason}")
        return allocation

    # -------------------------
    # DELETE (RESTRICTED)
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_payment_allocation(allocation: PaymentAllocation) -> None:
        if allocation.status == "APPLIED":
            raise ValueError("Applied allocations cannot be deleted.")

        allocation_id = allocation.id
        allocation.delete()

        logger.info(f"PaymentAllocation deleted | id={allocation_id}")

    # -------------------------
    # ATTACH / DETACH RELATIONS
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def attach_allocation_to_customer(allocation: PaymentAllocation, customer_id: int) -> PaymentAllocation:
        if customer_id is None:
            raise ValueError("Customer ID cannot be None.")
        allocation.customer_id = customer_id
        allocation.save(update_fields=["customer_id"])
        logger.info(f"PaymentAllocation '{allocation.id}' attached to Customer '{customer_id}'.")
        return allocation

    @staticmethod
    @db_transaction.atomic
    def detach_allocation_from_customer(allocation: PaymentAllocation) -> PaymentAllocation:
        allocation.customer = None
        allocation.save(update_fields=["customer"])
        logger.info(f"PaymentAllocation '{allocation.id}' detached from Customer.")
        return allocation

    # -------------------------
    # STATUS MANAGEMENT
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_payment_allocation_status(allocation: PaymentAllocation, new_status: str) -> PaymentAllocation:
        if new_status not in PaymentAllocationService.ALLOWED_STATUSES:
            logger.error(f"Invalid status '{new_status}' for allocation '{allocation.id}'.")
            raise ValueError(f"Invalid status: {new_status}")

        allowed_next = PaymentAllocationService.ALLOWED_TRANSITIONS.get(allocation.status, set())
        if new_status not in allowed_next:
            raise ValueError(f"Cannot transition from {allocation.status} to {new_status}")

        allocation.status = new_status
        allocation.save(update_fields=["status"])
        logger.info(f"PaymentAllocation '{allocation.id}' status updated to '{new_status}'.")
        return allocation
