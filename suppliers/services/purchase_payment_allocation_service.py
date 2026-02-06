from suppliers.models.purchase_payment_allocation_model import PurchasePaymentAllocation
from suppliers.models.purchase_invoice_model import PurchaseInvoice
from suppliers.models.supplier_model import Supplier
from loguru import logger
from django.db import transaction as db_transaction
from django.core.exceptions import ValidationError



class PurchasePaymentAllocationService:
    ALLOWED_UPDATE_FIELDS = {"amount", "notes", "allocation_date"}

    @staticmethod
    @db_transaction.atomic
    def create_allocation(**kwargs) -> PurchasePaymentAllocation:
        allocation = PurchasePaymentAllocation(**kwargs)
        allocation.allocation_number = allocation.generate_allocation_number()

        try:
            allocation.clean()  # Model-level validation
            PurchasePaymentAllocationService.validate_allocation(allocation)
        except ValidationError as e:
            logger.error(f"Validation failed for allocation: {e}")
            raise

        allocation.save()
        logger.info(
            f"Purchase Payment Allocation '{allocation.id}' created for "
            f"Payment '{allocation.purchase_payment.id}' and Invoice '{allocation.purchase_invoice.id}'."
        )
        return allocation

    @staticmethod
    @db_transaction.atomic
    def update_allocation(allocation: PurchasePaymentAllocation, **kwargs) -> PurchasePaymentAllocation:
        for key, value in kwargs.items():
            if key in PurchasePaymentAllocationService.ALLOWED_UPDATE_FIELDS:
                setattr(allocation, key, value)

        try:
            allocation.clean()
            PurchasePaymentAllocationService.validate_allocation(allocation)
        except ValidationError as e:
            logger.error(f"Validation failed for allocation '{allocation.id}': {e}")
            raise

        allocation.save()
        logger.info(
            f"Purchase Payment Allocation '{allocation.id}' updated for "
            f"Payment '{allocation.purchase_payment.id}' and Invoice '{allocation.purchase_invoice.id}'."
        )
        return allocation

    @staticmethod
    @db_transaction.atomic
    def delete_allocation(allocation: PurchasePaymentAllocation) -> None:
        allocation_id = allocation.id
        allocation.delete()
        logger.info(f"Purchase Payment Allocation '{allocation_id}' deleted.")

    @staticmethod
    def validate_allocation(allocation: PurchasePaymentAllocation) -> None:
        invoice = allocation.purchase_invoice
        payment = allocation.purchase_payment

        if allocation.amount <= 0:
            raise ValidationError("Allocation amount must be positive.")
        if allocation.amount > invoice.outstanding_amount:
            raise ValidationError("Allocation amount exceeds invoice outstanding amount.")
        if allocation.amount > payment.available_amount:
            raise ValidationError("Allocation amount exceeds payment available amount.")

    

    