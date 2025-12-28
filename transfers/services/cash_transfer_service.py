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
        branch: Branch,
        source_branch: Branch,
        destination_branch: Branch,
        source_branch_account: BranchAccount,
        destination_branch_account: BranchAccount,
        amount: Decimal,
        notes: str | None = None

    ) -> CashTransfer:
        cash_transfer = CashTransfer.objects.create(
            transfer=transfer,
            company=company,
            branch=branch,
            source_branch=source_branch,
            destination_branch=destination_branch,
            source_branch_account=source_branch_account,
            destination_branch_account=destination_branch_account,
            amount=amount,
            notes=notes
        )
        logger.info(
            f"Cash Transfer '{cash_transfer.id}' created for Transfer '{transfer.transfer_number}'."
        )
        TransferService.recalculate_transfer_totals(transfer)
        return cash_transfer

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_cash_transfer(
        cash_transfer: CashTransfer,
        *,
        amount: Decimal | None = None,
        notes: str | None = None
    ) -> CashTransfer:
        updated_fields = []
        if amount is not None:
            cash_transfer.amount = amount
            updated_fields.append("amount")
        if notes is not None:
            cash_transfer.notes = notes
            updated_fields.append("notes")

        if updated_fields:
            cash_transfer.save(update_fields=updated_fields)
            logger.info(f"Cash Transfer '{cash_transfer.id}' updated: {', '.join(updated_fields)}")
            if cash_transfer.transfer:
                TransferService.recalculate_transfer_totals(cash_transfer.transfer)

        return cash_transfer

    # -------------------------
    # DELETE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def delete_cash_transfer(cash_transfer: CashTransfer) -> None:
        transfer = cash_transfer.transfer
        transfer_number = cash_transfer.transfer.transfer_number if cash_transfer.transfer else 'None'
        cash_transfer_id = cash_transfer.id
        cash_transfer.delete()
        logger.info(f"Cash Transfer '{cash_transfer_id}' deleted from Transfer '{transfer_number}'.")

        if transfer:
            TransferService.recalculate_transfer_totals(transfer)

    # -------------------------
    # ATTACH / DETACH
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def attach_to_transfer(cash_transfer: CashTransfer, transfer: Transfer) -> CashTransfer:
        previous_transfer = cash_transfer.transfer
        cash_transfer.transfer = transfer
        cash_transfer.save(update_fields=['transfer'])
        logger.info(
            f"Cash Transfer '{cash_transfer.id}' attached to Transfer '{transfer.transfer_number}' "
            f"(previous transfer: '{previous_transfer.transfer_number if previous_transfer else 'None'}')."
        )

        if previous_transfer:
            TransferService.recalculate_transfer_totals(previous_transfer)
        TransferService.recalculate_transfer_totals(transfer)

        return cash_transfer

    @staticmethod
    @db_transaction.atomic
    def detach_from_transfer(cash_transfer: CashTransfer) -> CashTransfer:
        previous_transfer = cash_transfer.transfer
        cash_transfer.transfer = None
        cash_transfer.save(update_fields=['transfer'])
        logger.info(
            f"Cash Transfer '{cash_transfer.id}' detached from Transfer "
            f"'{previous_transfer.transfer_number if previous_transfer else 'None'}'."
        )

        if previous_transfer:
            TransferService.recalculate_transfer_totals(previous_transfer)
        return cash_transfer

    # -------------------------
    # HOLD / RELEASE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def hold_cash_transfer(cash_transfer: CashTransfer) -> CashTransfer:
        cash_transfer.status = CashTransfer.STATUS_HOLD
        cash_transfer.save(update_fields=['status'])
        logger.info(f"Cash Transfer '{cash_transfer.id}' is now on hold.")

        if cash_transfer.transfer:
            TransferService.recalculate_transfer_totals(cash_transfer.transfer)
        return cash_transfer

    @staticmethod
    @db_transaction.atomic
    def release_cash_transfer(cash_transfer: CashTransfer) -> CashTransfer:
        cash_transfer.status = CashTransfer.STATUS_RELEASED
        cash_transfer.save(update_fields=['status'])
        logger.info(f"Cash Transfer '{cash_transfer.id}' has been released from hold.")

        if cash_transfer.transfer:
            TransferService.recalculate_transfer_totals(cash_transfer.transfer)
        return cash_transfer