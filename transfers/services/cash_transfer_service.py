from transfers.models.cash_transfer_model import CashTransfer
from transfers.models.transfer_model import Transfer
from django.db import transaction as db_transaction
from loguru import logger
from transfers.services.transfer_service import TransferService  # for recalculating totals
from company.models import Company
from branch.models import Branch
from accounts.models import BranchAccount
from decimal import Decimal


class CashTransferError(Exception):
    """Custom exception for CashTransfer domain errors."""
    pass


class CashTransferService:

    ALLOWED_UPDATE_FIELDS = {"amount", "notes"}

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def create_cash_transfer(
        *,
        transfer: Transfer,
        company: Company,
        source_branch_account: BranchAccount,
        destination_branch_account: BranchAccount,
        total_amount: Decimal,
        notes: str | None = None

    ) -> CashTransfer:
        """Creates a new CashTransfer instance."""
        cash_transfer: CashTransfer = CashTransfer.objects.create(
            transfer=transfer,
            company=company,
            source_branch_account=source_branch_account,
            destination_branch_account=destination_branch_account,
            total_amount=total_amount,
            notes=notes
        )
        logger.info(
            f"Cash Transfer '{cash_transfer.pk}' created for Transfer '{transfer.reference_number}'."
        )
        CashTransferService.add_to_transfer(cash_transfer, transfer)
        return cash_transfer

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_cash_transfer(
        cash_transfer: CashTransfer,
        *,
        total_amount: Decimal | None = None,
        notes: str | None = None
    ) -> CashTransfer:
        """Updates the specified fields of the CashTransfer."""
        updated_fields = []
        if total_amount is not None:
            cash_transfer.total_amount = total_amount
            updated_fields.append("total_amount")
        if notes is not None:
            cash_transfer.notes = notes
            updated_fields.append("notes")

        if updated_fields:
            cash_transfer.save(update_fields=updated_fields)
            logger.info(f"Cash Transfer '{cash_transfer.pk}' updated: {', '.join(updated_fields)}")
            transfer: Transfer = cash_transfer.transfer
            if transfer:
                transfer.update_total_amount()

        return cash_transfer
    

    @staticmethod
    def get_cash_transfer(source_account, destination_account, transfer) -> CashTransfer:
        """Retrieve a CashTransfer by source, destination accounts and transfer."""
        try:
            cash_transfer = CashTransfer.objects.get(
                source_branch_account=source_account,
                destination_branch_account=destination_account,
                transfer=transfer
            )
            return cash_transfer
        except CashTransfer.DoesNotExist:
            logger.error(
                f"Cash Transfer not found for source '{source_account.pk}', "
                f"destination '{destination_account.pk}', transfer '{transfer.reference_number}'."
            )
            raise

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_cash_transfer(cash_transfer: CashTransfer) -> None:
        transfer: Transfer = cash_transfer.transfer
        transfer_number = cash_transfer.transfer.reference_number if cash_transfer.transfer else 'None'
        cash_transfer_id = cash_transfer.pk
        cash_transfer.delete()
        logger.info(f"Cash Transfer '{cash_transfer_id}' deleted from Transfer '{transfer_number}'.")

        if transfer:
            transfer.update_total_amount()


    # -------------------------
    # ATTACH / DETACH
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def add_to_transfer(cash_transfer: CashTransfer, transfer: Transfer) -> CashTransfer:
        """Adds the CashTransfer to the specified Transfer."""
        cash_transfer.transfer = transfer
        cash_transfer.save(update_fields=['transfer'])
        logger.info(
            f"Cash Transfer '{cash_transfer.pk}' added to Transfer '{transfer.reference_number}' "
        )

        transfer.update_total_amount()
        return cash_transfer


    @staticmethod
    @db_transaction.atomic
    def remove_from_transfer(cash_transfer: CashTransfer) -> CashTransfer:
        """
        Removes the CashTransfer from its associated Transfer.
        """
        previous_transfer: Transfer = cash_transfer.transfer
        cash_transfer.transfer = None
        cash_transfer.save(update_fields=['transfer'])
        logger.info(
            f"Cash Transfer '{cash_transfer.pk}' removed from Transfer "
            f"'{previous_transfer.reference_number if previous_transfer else 'None'}'."
        )
        transfer: Transfer = previous_transfer
        if transfer:
            transfer.update_total_amount()
        return cash_transfer