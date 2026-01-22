from transfers.services.transfer_service import TransferService
from transfers.models.transfer_model import Transfer


def reverse_transfer_util(
        *,
        company,
        branch,
        reference_number
) -> Transfer:
    """
    Utility function to reverse a transfer.
    """
    transfer = TransferService.get_transfer(
        company=company,
        branch=branch,
        reference_number=reference_number
    )
    return TransferService.reverse_transfer(transfer)