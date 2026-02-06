from transfers.services.cash_service.cash_transfer_service import CashTransferService
from transfers.models.cash_transfer_model import CashTransfer


def add_cash_transfer_to_transfer_util(
        *,
        cash_transfer: CashTransfer,
        transfer,
) -> CashTransfer:
    """
    Utility function to add a cash transfer to a transfer.
    """

    CashTransferService.add_to_transfer(
        cash_transfer=cash_transfer,
        transfer=transfer
    )
    return cash_transfer