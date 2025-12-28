from transfers.models.product_transfer_model import ProductTransfer
from transfers.models.transfer_model import Transfer
from django.db import transaction as db_transaction
from loguru import logger
from transfers.services.transfer_service import TransferService
from company.models import Company
from branch.models import Branch
from inventory.models import Product
from users.models.user_model import User


class ProductTransferError(Exception):
    """Custom exception for ProductTransfer domain errors."""
    pass

class ProductTransferService:

    STATUS_PENDING = "PENDING"
    STATUS_TRANSFERRED = "TRANSFERRED"
    STATUS_CANCELLED = "CANCELLED"

    VALID_STATUSES = {STATUS_PENDING, STATUS_TRANSFERRED, STATUS_CANCELLED}

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def create_product_transfer(
        *,
        transfer: Transfer | None,
        company: Company,
        branch: Branch,
        source_branch: Branch | None,
        destination_branch: Branch | None,
        product: Product,
        quantity: int,
        unit_price: float | None = None,
        total_price: float | None = None,
        notes: str = "",
        created_by: User | None = None
    ) -> ProductTransfer:

        product_transfer = ProductTransfer.objects.create(
            transfer=transfer,
            company=company,
            branch=branch,
            source_branch=source_branch,
            destination_branch=destination_branch,
            product=product,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price,
            notes=notes
        )

        logger.info(
            f"Product Transfer '{product_transfer.id}' created "
            f"for Transfer '{transfer.transfer_number if transfer else 'None'}'."
        )

        TransferService.recalculate_total(transfer) if transfer else None
        return product_transfer

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_product_transfer(
        product_transfer: ProductTransfer,
        *,
        product: Product | None = None,
        quantity: int | None = None,
        unit_price: float | None = None,
        total_price: float | None = None,
        notes: str | None = None,
        source_branch: Branch | None = None,
        destination_branch: Branch | None = None
    ) -> ProductTransfer:

        updated_fields = []

        if product is not None:
            product_transfer.product = product
            updated_fields.append("product")
        if quantity is not None:
            product_transfer.quantity = quantity
            updated_fields.append("quantity")
        if unit_price is not None:
            product_transfer.unit_price = unit_price
            updated_fields.append("unit_price")
        if total_price is not None:
            product_transfer.total_price = total_price
            updated_fields.append("total_price")
        if notes is not None:
            product_transfer.notes = notes
            updated_fields.append("notes")
        if source_branch is not None:
            product_transfer.source_branch = source_branch
            updated_fields.append("source_branch")
        if destination_branch is not None:
            product_transfer.destination_branch = destination_branch
            updated_fields.append("destination_branch")

        if updated_fields:
            product_transfer.save(update_fields=updated_fields)
            logger.info(
                f"Product Transfer '{product_transfer.id}' updated: {', '.join(updated_fields)}"
            )

            if product_transfer.transfer:
                TransferService.recalculate_total(product_transfer.transfer)

        return product_transfer

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_product_transfer(product_transfer: ProductTransfer) -> None:
        transfer_number = product_transfer.transfer.transfer_number if product_transfer.transfer else 'None'
        product_transfer_id = product_transfer.id
        product_transfer.delete()
        logger.info(f"Product Transfer '{product_transfer_id}' deleted from Transfer '{transfer_number}'.")

        if product_transfer.transfer:
            TransferService.recalculate_total(product_transfer.transfer)



    @staticmethod
    @db_transaction.atomic
    def reverse_product_transfer(product_transfer: ProductTransfer) -> ProductTransfer:
        """
        Reverses a product transfer by swapping source and destination branches.
        """
        original_source = product_transfer.source_branch
        original_destination = product_transfer.destination_branch

        product_transfer.source_branch = original_destination
        product_transfer.destination_branch = original_source

        product_transfer.save(update_fields=['source_branch', 'destination_branch'])
        logger.info(
            f"Product Transfer '{product_transfer.id}' reversed: "
            f"{original_source} <-> {original_destination}"
        )

        if product_transfer.transfer:
            TransferService.recalculate_total(product_transfer.transfer)

        return product_transfer
    

    @staticmethod
    @db_transaction.atomic
    def attach_to_product_transfer(
        product_transfer: ProductTransfer,
        transfer: Transfer
    ) -> ProductTransfer:
        product_transfer.transfer = transfer
        product_transfer.save(update_fields=['transfer'])
        logger.info(
            f"Product Transfer '{product_transfer.id}' attached to Transfer '{transfer.reference_number}'."
        )
        TransferService.recalculate_total(transfer)
        return product_transfer
    

    @staticmethod
    @db_transaction.atomic
    def detach_from_product_transfer(
        product_transfer: ProductTransfer
    ) -> ProductTransfer:
        previous_transfer = product_transfer.transfer
        product_transfer.transfer = None
        product_transfer.save(update_fields=['transfer'])
        logger.info(
            f"Product Transfer '{product_transfer.id}' detached from Transfer "
            f"'{previous_transfer.transfer_number if previous_transfer else 'None'}'."
        )

        if previous_transfer:
            TransferService.recalculate_total(previous_transfer)
        return product_transfer