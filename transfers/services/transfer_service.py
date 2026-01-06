from branch.services.branch_service import BranchService
from accounts.services.branch_account_service import BranchAccountService
from transactions.services.transaction_service import TransactionService
from transfers.models.transfer_model import Transfer
from django.db import transaction as db_transaction
from loguru import logger
from users.models import User
from company.models import Company
from branch.models import Branch
from django.db.models import F, Sum, FloatField
from inventory.services.product_stock_service import ProductStockService
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
    # RECALCULATE TOTAL
    # -------------------------

    

    @staticmethod
    @db_transaction.atomic
    def recalculate_total(transfer: Transfer):
        """
        Recalculate the total_amount for a transfer based on its type:
        - For product transfers: sum(quantity * unit_price) of all items.
        - For cash transfers: use the cash_transfer.amount.
        """
        if transfer.type == "product":
            # Ensure a ProductTransfer exists
            if hasattr(transfer, "product_transfer") and transfer.product_transfer:
                total = transfer.product_transfer.items.aggregate(
                    total_amount=Sum(F('quantity') * F('unit_price'), output_field=FloatField())
                ).get('total_amount') or 0
                transfer.total_amount = total
                transfer.save(update_fields=['total_amount'])
                logger.info(f"Product Transfer '{transfer.reference_number}' total recalculated: {total}")

        elif transfer.type == "cash":
            # Ensure a CashTransfer exists
            if hasattr(transfer, "cash_transfer") and transfer.cash_transfer:
                transfer.total_amount = transfer.cash_transfer.total_amount
                transfer.save(update_fields=['total_amount'])
                logger.info(f"Cash Transfer '{transfer.reference_number}' total updated: {transfer.total_amount}")
    

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


        if transfer.type == 'product':
            if not transfer.items.exists():
                raise ValueError("Cannot perform product transfer without attached product items")

            # Recalculate totals
            TransferService.recalculate_total(transfer)

            if transfer.total_amount <= 0:
                raise ValueError("Transfer amount must be greater than zero")

            # Move Stock
            ProductStockService.decrease_stock_for_transfer(transfer)
            ProductStockService.increase_stock_for_transfer(transfer)
        
        elif transfer.type == 'cash':

            TransferService.recalculate_total(transfer)

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
            branch=transfer.branch,
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



    