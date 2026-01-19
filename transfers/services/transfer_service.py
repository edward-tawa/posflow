from branch.services.branch_service import BranchService
from accounts.services.branch_account_service import BranchAccountService
from transactions.services.transaction_service import TransactionService
from inventory.services.product_stock_service import ProductStockService
from transfers.models.transfer_model import Transfer
from django.db import transaction as db_transaction
from users.models import User
from company.models import Company
from branch.models import Branch
from django.db.models import F, Sum, FloatField
from loguru import logger
from datetime import date


class TransferService:

    ALLOWED_UPDATE_FIELDS = {"status", "amount", "source", "destination"}
    VALID_STATUSES = {"pending", "completed", "cancelled"}

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def create_transfer(
        *,
        company: Company,
        branch: Branch,
        transferred_by: User | None = None,
        received_by: User | None = None,
        sent_by: User | None = None,
        transfer_date: date | None = None,
        notes: str = "",
        type: str = "cash",
        status: str = "pending"
    ) -> Transfer:
        transfer = Transfer.objects.create(
            company=company,
            branch=branch,
            transferred_by=transferred_by,
            received_by=received_by,
            sent_by=sent_by,
            transfer_date=transfer_date or date.today(),
            notes=notes,
            type=type,
            status=status
        )
        logger.info(f"Transfer '{transfer.reference_number}' created.")
        return transfer
    
    @staticmethod
    @db_transaction.atomic
    def get_transfer(
        *,
        company: Company,
        branch: Branch,
        reference_number: str
    ) -> Transfer:
        transfer = Transfer.objects.get(
            company=company,
            branch=branch,
            reference_number=reference_number,
        )
        return transfer

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_transfer(
        transfer: Transfer,
        *,
        status: str | None = None,
        notes: str | None = None,
        type: str | None = None,
        transferred_by: User | None = None,
        received_by: User | None = None,
        sent_by: User | None = None,
        transfer_date: date | None = None
    ) -> Transfer:
        updated_fields = []

        if status is not None:
            if status not in TransferService.VALID_STATUSES:
                raise ValueError(f"Invalid transfer status: {status}")
            transfer.status = status
            updated_fields.append("status")

        if notes is not None:
            transfer.notes = notes
            updated_fields.append("notes")

        if type is not None:
            transfer.type = type
            updated_fields.append("type")

        if transferred_by is not None:
            transfer.transferred_by = transferred_by
            updated_fields.append("transferred_by")

        if received_by is not None:
            transfer.received_by = received_by
            updated_fields.append("received_by")

        if sent_by is not None:
            transfer.sent_by = sent_by
            updated_fields.append("sent_by")

        if transfer_date is not None:
            transfer.transfer_date = transfer_date
            updated_fields.append("transfer_date")

        if updated_fields:
            transfer.save(update_fields=updated_fields)
            logger.info(f"Transfer '{transfer.reference_number}' updated: {updated_fields}")

        return transfer

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_transfer(transfer: Transfer) -> None:
        transfer_number = transfer.reference_number
        transfer.delete()
        logger.info(f"Transfer '{transfer_number}' deleted.")
    

    # -------------------------
    # HOLD / RELEASE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def hold_transfer(transfer: Transfer) -> Transfer:
        if transfer.status in ["completed", "cancelled"]:
            raise ValueError("Cannot put a completed or cancelled transfer on hold.")

        transfer.status = "on_hold"
        transfer.save(update_fields=['status'])
        logger.info(f"Transfer '{transfer.reference_number}' is now on hold.")
        return transfer

    @staticmethod
    @db_transaction.atomic
    def release_transfer(transfer: Transfer) -> Transfer:
        if transfer.status != "on_hold":
            raise ValueError("Only transfers on hold can be released.")

        # Decide what status it goes to after release. Here, we revert to 'pending'
        transfer.status = "pending"
        transfer.save(update_fields=['status'])
        logger.info(f"Transfer '{transfer.reference_number}' has been released from hold.")
        return transfer


    @staticmethod
    @db_transaction.atomic
    def perform_transfer(transfer: Transfer):
        """
        Perform a product transfer: record transaction, update stock,
        then mark transfer completed.
        """

        # Guards by checking transfer status and items
        if transfer.status != "pending":
            raise ValueError("Only pending transfers can be performed")


        if transfer.type.lower() == 'product':
            if not transfer.items.exists():
                raise ValueError("Cannot perform product transfer without attached product items")

            # Recalculate totals
            transfer.update_total_amount()

            if transfer.total_amount <= 0:
                raise ValueError("Transfer amount must be greater than zero")
            
            # Move Stock
            ProductStockService.decrease_stock_for_transfer(transfer)
            ProductStockService.increase_stock_for_transfer(transfer)
        
        elif transfer.type.lower() == 'cash':

            transfer.update_total_amount()

            if transfer.total_amount <= 0:
                raise ValueError("Transfer amount must be greater than zero")
            
        else:
            logger.error(f"Unknown transfer type encountered or selected: {transfer.type}")
            raise ValueError(f"Unknown transfer type: {transfer.type}")
            

        # Retrieve branch accounts
        source_branch_account = BranchAccountService.create_or_get_branch_account(
            branch=transfer.source_branch,
            company=transfer.company
        )
        dest_branch_account = BranchAccountService.create_or_get_branch_account(
            branch=transfer.destination_branch,
            company=transfer.company
        )
        
        # Record Transaction
        transaction = TransactionService.create_transaction(
            company=transfer.company,
            branch=transfer.source_branch,  # assigned to source branch because that's where it originates
            debit_account=dest_branch_account,
            credit_account=source_branch_account,
            transaction_type=f'{transfer.type.upper()}_TRANSFER',
            transaction_category=f'{transfer.type.upper()}_TRANSFER',
            total_amount=transfer.total_amount,
            supplier=None,
            customer=None,
        )
        TransactionService.apply_transaction_to_accounts(transaction)


        # Mark completed
        transfer.status = 'completed'
        transfer.save(update_fields=['status'])

        logger.info(
            f"{transfer.type.capitalize()} Transfer '{transfer.reference_number}' performed successfully."
        )

        return transfer


    
    @staticmethod
    @db_transaction.atomic
    def reverse_transfer(transfer: Transfer) -> Transfer:
        """
        Reverses a transfer by swapping source and destination branches.
        """
        original_source = transfer.source_branch
        original_destination = transfer.destination_branch

        transfer.source_branch = original_destination
        transfer.destination_branch = original_source

        transfer.save(update_fields=['source_branch', 'destination_branch'])

        if transfer.type.lower() == 'product':
            ProductStockService.decrease_stock_for_transfer(transfer)
            ProductStockService.increase_stock_for_transfer(transfer)

        source_branch_account = BranchAccountService.create_or_get_branch_account(
            branch=original_destination,
            company=transfer.company
        )
        dest_branch_account = BranchAccountService.create_or_get_branch_account(
            branch=original_source,
            company=transfer.company
        )

         # Record Transaction
        transaction = TransactionService.create_transaction(
            company=transfer.company,
            branch=transfer.source_branch,  # assigned to source branch because that's where it originates
            debit_account=dest_branch_account,
            credit_account=source_branch_account,
            transaction_type='PRODUCT_TRANSFER',
            transaction_category='PRODUCT_TRANSFER',
            total_amount=transfer.total_amount,
            supplier=None,
            customer=None,
        )
        TransactionService.apply_transaction_to_accounts(transaction)

        logger.info(
            f"Transfer '{transfer.id}' reversed: "
            f"{original_source} <-> {original_destination}"
        )

        if transfer:
            transfer.update_total_amount()
        return transfer