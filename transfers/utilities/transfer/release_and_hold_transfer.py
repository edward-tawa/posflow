from transfers.services.transfer_service import TransferService
from transfers.models.transfer_model import Transfer



def hold_transfer_util(
        *,
        company,
        branch,
        reference_number
) -> Transfer:
    """
    Utility function to hold a transfer.
    """
    transfer = TransferService.get_transfer(
        company=company,
        branch=branch,
        reference_number=reference_number
    )
    return TransferService.hold_transfer(transfer)





def release_transfer_util(
        *,
        company,
        branch,
        reference_number
) -> Transfer:
    """
    Utility function to release a transfer.
    """
    transfer = TransferService.get_transfer(
        company=company,
        branch=branch,
        reference_number=reference_number
    )
    return TransferService.release_transfer(transfer)