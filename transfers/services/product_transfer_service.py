from transfers.models.product_transfer_model import ProductTransfer
from transfers.models.transfer_model import Transfer
from django.db import transaction as db_transaction
from loguru import logger
from transfers.services.transfer_service import TransferService  # Assuming it's in services

class ProductTransferError(Exception):
    """Custom exception for ProductTransfer domain errors."""
    pass

class ProductTransferService:

    ALLOWED_UPDATE_FIELDS = {"product", "quantity", "unit_price", "total_price", "notes"}
    STATUS_PENDING = "PENDING"
    STATUS_TRANSFERRED = "TRANSFERRED"
    STATUS_CANCELLED = "CANCELLED"
    VALID_STATUSES = {STATUS_PENDING, STATUS_TRANSFERRED, STATUS_CANCELLED}

    @staticmethod
    @db_transaction.atomic
    def create_product_transfer(**kwargs) -> ProductTransfer:
        product_transfer = ProductTransfer.objects.create(**kwargs)
        logger.info(
            f"Product Transfer '{product_transfer.id}' created "
            f"for Transfer '{product_transfer.transfer.transfer_number if product_transfer.transfer else 'None'}'."
        )
        return product_transfer

    @staticmethod
    @db_transaction.atomic
    def update_product_transfer(product_transfer: ProductTransfer, **kwargs) -> ProductTransfer:
        updated_fields = []

        for key, value in kwargs.items():
            if key in ProductTransferService.ALLOWED_UPDATE_FIELDS:
                setattr(product_transfer, key, value)
                updated_fields.append(key)
            else:
                raise ProductTransferError(f"Field '{key}' cannot be updated.")

        if not updated_fields:
            return product_transfer  # Nothing to update

        product_transfer.save(update_fields=updated_fields)
        logger.info(f"Product Transfer '{product_transfer.id}' updated: {', '.join(updated_fields)}")

        # Optional: propagate update to parent Transfer totals
        if product_transfer.transfer:
            TransferService.recalculate_transfer_totals(product_transfer.transfer)

        return product_transfer

    @staticmethod
    @db_transaction.atomic
    def delete_product_transfer(product_transfer: ProductTransfer) -> None:
        transfer_number = product_transfer.transfer.transfer_number if product_transfer.transfer else 'None'
        product_transfer_id = product_transfer.id
        product_transfer.delete()
        logger.info(f"Product Transfer '{product_transfer_id}' deleted from Transfer '{transfer_number}'.")

        # Optional: update parent Transfer totals
        if product_transfer.transfer:
            TransferService.recalculate_transfer_totals(product_transfer.transfer)

    @staticmethod
    @db_transaction.atomic
    def attach_to_transfer(product_transfer: ProductTransfer, transfer: Transfer) -> ProductTransfer:
        previous_transfer = product_transfer.transfer
        product_transfer.transfer = transfer
        product_transfer.save(update_fields=['transfer'])
        logger.info(
            f"Product Transfer '{product_transfer.id}' attached to Transfer '{transfer.transfer_number}' "
            f"(previous transfer: '{previous_transfer.transfer_number if previous_transfer else 'None'}')."
        )

        # Recalculate totals for both transfers
        if previous_transfer:
            TransferService.recalculate_transfer_totals(previous_transfer)
        TransferService.recalculate_transfer_totals(transfer)

        return product_transfer

    @staticmethod
    @db_transaction.atomic
    def detach_from_transfer(product_transfer: ProductTransfer) -> ProductTransfer:
        if not product_transfer.transfer:
            return product_transfer  # Already detached

        previous_transfer = product_transfer.transfer
        product_transfer.transfer = None
        product_transfer.save(update_fields=['transfer'])
        logger.info(
            f"Product Transfer '{product_transfer.id}' detached from Transfer '{previous_transfer.transfer_number}'."
        )

        # Update previous transfer totals
        TransferService.recalculate_transfer_totals(previous_transfer)
        return product_transfer

    @staticmethod
    @db_transaction.atomic
    def transfer_product(product_transfer: ProductTransfer) -> ProductTransfer:
        if not product_transfer.transfer:
            raise ProductTransferError("Product Transfer must be attached to a Transfer to be processed.")

        product_transfer.status = ProductTransferService.STATUS_TRANSFERRED
        product_transfer.save(update_fields=['status'])
        logger.info(f"Product Transfer '{product_transfer.id}' marked as {ProductTransferService.STATUS_TRANSFERRED}.")

        # Recalculate parent Transfer totals and possibly update its status
        TransferService.recalculate_transfer_totals(product_transfer.transfer)
        return product_transfer
