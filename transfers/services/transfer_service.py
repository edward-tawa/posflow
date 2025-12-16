from transfers.models.transfer_model import Transfer
from django.db import transaction as db_transaction
from loguru import logger



class TransferService:

    ALLOWED_UPDATE_FIELDS = {"status", "amount", "source", "destination"}
    VALID_STATUSES = {"pending", "completed", "cancelled"}

    @staticmethod
    @db_transaction.atomic
    def create_transfer(**kwargs) -> Transfer:
        transfer = Transfer.objects.create(**kwargs)
        logger.info(f"Transfer '{transfer.transfer_number}' created.")
        return transfer

    @staticmethod
    @db_transaction.atomic
    def update_transfer(transfer: Transfer, **kwargs) -> Transfer:
        if not kwargs:
            return transfer

        for key, value in kwargs.items():
            if key not in TransferService.ALLOWED_UPDATE_FIELDS:
                raise ValueError(f"Field '{key}' cannot be updated")
            setattr(transfer, key, value)

        transfer.save(update_fields=kwargs.keys())
        logger.info(f"Transfer '{transfer.transfer_number}' updated.")
        return transfer

    @staticmethod
    @db_transaction.atomic
    def update_transfer_status(transfer: Transfer, new_status: str) -> Transfer:
        if new_status not in TransferService.VALID_STATUSES:
            raise ValueError(f"Invalid transfer status: {new_status}")

        transfer.status = new_status
        transfer.save(update_fields=["status"])
        logger.info(
            f"Transfer '{transfer.transfer_number}' status updated to '{new_status}'."
        )
        return transfer

    @staticmethod
    @db_transaction.atomic
    def delete_transfer(transfer: Transfer) -> None:
        transfer_number = transfer.transfer_number
        transfer.delete()
        logger.info(f"Transfer '{transfer_number}' deleted.")
