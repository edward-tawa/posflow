from transfers.services.transfer_service import TransferService
from transfers.models.transfer_model import Transfer



def perform_transfer_util(
        *,
        company,
        branch,
        reference_number
) -> Transfer:
    """
    Utility function to perform a transfer.
    """
    transfer = TransferService.get_transfer(
        company=company,
        branch=branch,
        reference_number=reference_number
    )
    return TransferService.perform_transfer(transfer)