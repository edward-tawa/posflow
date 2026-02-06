from branch.models.branch_model import Branch
from transfers.models.cash_transfer_model import CashTransfer
from transfers.services.cash_service.adjust_cash_balances_service import AdjustCashBalancesService
from transfers.services.cash_service.cash_transfer_service import CashTransferService
from transfers.models.transfer_model import Transfer
from transfers.services.transfer_service import TransferService
from transactions.services.transaction_service import TransactionService
from accounts.services.branch_account_service import BranchAccountService
from transactions.models.transaction_model import Transaction
from company.models.company_model import Company
from branch.models.branch_model import Branch
from dataclasses import dataclass
from loguru import logger
from decimal import Decimal
from django.db import transaction as db_transaction



class ProcessCashTransferService:
    # -------------------------
    # PROCESS CASH TRANSFER
    # -------------------------

    @staticmethod
    @db_transaction.atomic
    def process_cash_transfer(
        *,
        transfer: Transfer,
        company: Company,
        source_branch: Branch,
        destination_branch: Branch,
        total_amount: Decimal,
    ) -> Transaction:
        """Processes a cash transfer by creating a cash transfer record and associated transaction."""
        try:
            # Create Cash Transfer
            cash_transfer = CashTransferService.create_cash_transfer(
                transfer=transfer,
                company=company,
                source_branch=source_branch,
                destination_branch=destination_branch,
                total_amount=total_amount,
            )

            # Get accounts
            source_branch_account = BranchAccountService.get_branch_account(
                company=company,
                branch=source_branch,
            )
            destination_branch_account = BranchAccountService.get_branch_account(
                company=company,
                branch=destination_branch,
            )

            # Adjust cash balances
            AdjustCashBalancesService.adjust_cash_balances(
                cash_transfer=cash_transfer,
                source_account=source_branch_account.account,
                destination_account=destination_branch_account.account,
                amount=total_amount,
            )

            # Create Transaction
            transaction = TransactionService.create_transaction(
                company=company,
                branch=source_branch,
                debit_account=destination_branch_account.account,
                credit_account=source_branch_account.account,
                transaction_type="CASH_TRANSFER",
                transaction_category="TRANSFER",
                total_amount=total_amount,
            )

            logger.info(
                f"Processed cash transfer | Transfer ID={transfer.pk} | "
                f"Amount={total_amount} | From={source_branch.name} | To={destination_branch.name}"
            )

            return transaction

        except Exception as e:
            logger.exception(
                f"Failed to process cash transfer | Transfer ID={transfer.pk} | Error={str(e)}"
            )
            raise