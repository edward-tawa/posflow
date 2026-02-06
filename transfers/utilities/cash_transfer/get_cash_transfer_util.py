from transfers.services.cash_service.cash_transfer_service import CashTransferService
from transfers.models.cash_transfer_model import CashTransfer


def get_cash_transfer_util(
        *,
        source_branch_account,
        destination_branch_account,
        transfer,
) -> CashTransfer:
    """
    Utility function to get a cash transfer by its ID.
    """
    cash_transfer = CashTransferService.get_cash_transfer(
        source_account=source_branch_account,
        destination_account=destination_branch_account,
        transfer=transfer
    )
    return cash_transfer