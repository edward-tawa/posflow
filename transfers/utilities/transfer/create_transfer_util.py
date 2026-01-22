from transfers.services.transfer_service import TransferService
from transfers.models.transfer_model import Transfer




def create_transfer_util(
        *,
        company,
        branch,
        transferred_by=None,
        received_by=None,
        sent_by=None,
        transfer_date=None,
        notes="",
        type="cash",
        status="pending"
) -> Transfer:
    """
    Utility function to create a transfer.
    """
    transfer = TransferService.create_transfer(
        company=company,
        branch=branch,
        transferred_by=transferred_by,
        received_by=received_by,
        sent_by=sent_by,
        transfer_date=transfer_date,
        notes=notes,
        type=type,
        status=status
    )
    return transfer