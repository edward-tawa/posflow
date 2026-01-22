from transfers.services.cash_transfer_service import CashTransferService
from transfers.models.cash_transfer_model import CashTransfer



def remove_cash_transfer_from_transfer_util(
        *,
        cash_transfer: CashTransfer
) -> CashTransfer:
    """
    Utility function to remove a cash transfer from a transfer.
    """

    CashTransferService.remove_from_transfer(
        cash_transfer=cash_transfer
    )
    return cash_transfer