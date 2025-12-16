from transfers.models.cash_transfer_model import CashTransfer
from transfers.models.transfer_model import Transfer
from django.db import transaction as db_transaction
from loguru import logger
from transfers.services.transfer_service import TransferService  # for recalculating totals

class CashTransferError(Exception):
    """Custom exception for CashTransfer domain errors."""
    pass

class CashTransferService:

    ALLOWED_UPDATE_FIELDS = {"amount", "currency", "notes"}
    STATUS_ON_HOLD = True
    STATUS_RELEASED = False

    @staticmethod
    @db_transaction.atomic
    def create_cash_transfer(**kwargs) -> CashTransfer:
        cash_transfer = CashTransfer.objects.create(**kwargs)
        logger.info(
            f"Cash Transfer '{cash_transfer.id}' created "
            f"for Transfer '{cash_transfer.transfer.transfer_number if cash_transfer.transfer else 'None'}'."
        )
        if cash_transfer.transfer:
            TransferService.recalculate_transfer_totals(cash_transfer.transfer)
        return cash_transfer

    @staticmethod
    @db_transaction.atomic
    def update_cash_transfer(cash_transfer: CashTransfer, **kwargs) -> CashTransfer:
        updated_fields = []
        for key, value in kwargs.items():
            if key in CashTransferService.ALLOWED_UPDATE_FIELDS:
                setattr(cash_transfer, key, value)
                updated_fields.append(key)
            else:
                raise CashTransferError(f"Field '{key}' cannot be updated.")

        if not updated_fields:
            return cash_transfer

        cash_transfer.save(update_fields=updated_fields)
        logger.info(f"Cash Transfer '{cash_transfer.id}' updated: {', '.join(updated_fields)}")

        if cash_transfer.transfer:
            TransferService.recalculate_transfer_totals(cash_transfer.transfer)
        return cash_transfer

    @staticmethod
    @db_transaction.atomic
    def delete_cash_transfer(cash_transfer: CashTransfer) -> None:
        transfer_number = cash_transfer.transfer.transfer_number if cash_transfer.transfer else 'None'
        cash_transfer_id = cash_transfer.id
        cash_transfer.delete()
        logger.info(f"Cash Transfer '{cash_transfer_id}' deleted from Transfer '{transfer_number}'.")

        if cash_transfer.transfer:
            TransferService.recalculate_transfer_totals(cash_transfer.transfer)

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

    @staticmethod
    @db_transaction.atomic
    def hold_cash_transfer(cash_transfer: CashTransfer) -> CashTransfer:
        cash_transfer.is_on_hold = CashTransferService.STATUS_ON_HOLD
        cash_transfer.save(update_fields=['is_on_hold'])
        logger.info(f"Cash Transfer '{cash_transfer.id}' is now on hold.")

        if cash_transfer.transfer:
            TransferService.recalculate_transfer_totals(cash_transfer.transfer)
        return cash_transfer

    @staticmethod
    @db_transaction.atomic
    def release_cash_transfer(cash_transfer: CashTransfer) -> CashTransfer:
        cash_transfer.is_on_hold = CashTransferService.STATUS_RELEASED
        cash_transfer.save(update_fields=['is_on_hold'])
        logger.info(f"Cash Transfer '{cash_transfer.id}' has been released from hold.")

        if cash_transfer.transfer:
            TransferService.recalculate_transfer_totals(cash_transfer.transfer)
        return cash_transfer
