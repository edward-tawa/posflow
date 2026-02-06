from accounts.services.branch_account_service import BranchAccountService
from transfers.models.product_transfer_model import ProductTransfer
from transfers.models.transfer_model import Transfer
from django.db import transaction as db_transaction
from transfers.exceptions.product_transfer.product_transfer_exception import (ProductTransferStatusError,
    ProductTransferNotAssigned,
    ProductTransferAlreadyAssigned) 
from loguru import logger
from company.models import Company
from branch.models import Branch
from inventory.models import Product
from users.models.user_model import User


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
        transfer: Transfer,
        company: Company,
        source_branch: Branch,
        destination_branch: Branch,
        notes: str = "",
        created_by: User | None = None
    ) -> ProductTransfer:
        
        if transfer is None:
            raise ValueError("Transfer must be provided to create a Product Transfer.")
        
        elif transfer.type.lower() != "product":
            raise ValueError("Cannot create Product Transfer for a non-product transfer.")
        
        elif source_branch is None or destination_branch is None:
            raise ValueError("Source and Destination branches must be provided.")
        

        product_transfer = ProductTransfer.objects.create(
            transfer=transfer,
            company=company,
            source_branch=source_branch,
            destination_branch=destination_branch,
            notes=notes,
            created_by=created_by
        )

        logger.info(
            f"Product Transfer '{product_transfer.id}' created "
            f"for Transfer '{transfer.reference_number if transfer else 'None'}'."
        )
        
        # Add product transfer to transfer
        ProductTransferService.add_to_transfer(product_transfer, transfer)

        transfer.update_total_amount()

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
                f"Product Transfer '{product_transfer.pk}' updated: {', '.join(updated_fields)}"
            )

            if product_transfer.transfer:
                transfer: Transfer = product_transfer.transfer
                transfer.update_total_amount()

        return product_transfer
    

    @staticmethod
    @db_transaction.atomic
    def get_product_transfer(
        *,
        company,
        source_branch: Branch,
        destination_branch: Branch,
        transfer: Transfer,
        ):
        """
        Fetches or creates a ProductTransfer record for a given product between two branches.

        Args:
            company: The company to which the transfer belongs.
            source_branch: The branch from which stock is transferred.
            destination_branch: The branch receiving the stock.
            product: The product being transferred.

        Returns:
            ProductTransfer instance (and optionally a boolean if created).
        """

        try:
            product_transfer = ProductTransfer.objects.get(
                company=company,
                source_branch=source_branch,
                destination_branch=destination_branch,
                transfer=transfer,
            )

            return product_transfer
    
        except ProductTransfer.DoesNotExist:
            logger.info(
                f"ProductTransfer does not exist for "
                f"Company: {company}, "
                f"Source Branch: {source_branch}, "
                f"Destination Branch: {destination_branch}, "
                f"Transfer: {transfer}."
            )
            raise


    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_product_transfer(product_transfer: ProductTransfer) -> None:
        transfer: Transfer = product_transfer.transfer  # keep a reference
        product_transfer_id = product_transfer.pk
        transfer_reference_number = transfer.reference_number if transfer else 'None'
        
        product_transfer.delete()
        logger.info(f"Product Transfer '{product_transfer_id}' deleted from Transfer '{transfer_reference_number}'.")

        if transfer:
            transfer.update_total_amount()


   

    @staticmethod
    @db_transaction.atomic
    def add_to_transfer(
        product_transfer: ProductTransfer,
        transfer: Transfer
    ) -> ProductTransfer:
        
        if transfer.status in {'completed', 'cancelled'}:
            raise ProductTransferStatusError(
                f"Cannot add Product Transfer to Transfer '{transfer.reference_number}' "
                f"as it is already '{transfer.status}'."
            )
        
        if product_transfer.transfer is not None:
            raise ProductTransferAlreadyAssigned(
                f"Product Transfer '{product_transfer.pk}' is already assigned to Transfer "
                f"'{product_transfer.transfer.reference_number}'."
            )
        
        product_transfer.transfer = transfer
        product_transfer.save(update_fields=['transfer'])
        logger.info(    
            f"Product Transfer '{product_transfer.pk}' added to Transfer '{transfer.reference_number}'."
        )
        transfer.update_total_amount()
        return product_transfer
    

    @staticmethod
    @db_transaction.atomic
    def remove_from_transfer(
        product_transfer: ProductTransfer,
        transfer: Transfer
    ) -> ProductTransfer:
        
        if product_transfer.transfer is None:
            raise ProductTransferNotAssigned("Can remove product transfer from trnasfer product trsanfer is not assigned to a transfer")
        
        previous_transfer: Transfer = product_transfer.transfer
        product_transfer.transfer = None
        product_transfer.save(update_fields=['transfer'])
        logger.info(
            f"Product Transfer '{product_transfer.pk}' removed from Transfer {transfer.reference_number}"
            f"'{previous_transfer.reference_number if previous_transfer else 'None'}'."
        )

        if previous_transfer:
            previous_transfer.update_total_amount()
        return product_transfer
    

    