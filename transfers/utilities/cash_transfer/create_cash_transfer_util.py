from transfers.services.cash_transfer_service import CashTransferService
from transfers.models.cash_transfer_model import CashTransfer


def create_cash_transfer_util(
        *,
        transfer,
        company,
        source_branch,
        destination_branch,
        source_branch_account,
        destination_branch_account,
        amount: float,
        notes: str | None = None,
) -> CashTransfer:
    """
    Utility function to create a cash transfer.
    """
    cash_transfer = CashTransferService.create_cash_transfer(
        transfer=transfer,
        company=company,
        amount=amount,
    )
    return cash_transfer