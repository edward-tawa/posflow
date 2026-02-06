from accounts.services.account_service import AccountService
from accounts.models.account_model import Account
from accounts.services.cash_account_service import CashAccountService
from branch.models.branch_model import Branch
from company.models.company_model import Company
from django.db import transaction as db_transaction
from loguru import logger
from decimal import Decimal
from transfers.models.cash_transfer_model import CashTransfer



class AdjustCashBalancesService:
    
    # -------------------------
    # ADJUST CASH BALANCES
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def adjust_cash_balances(
        *,
        cash_transfer: CashTransfer,
        source_account: Account,
        destination_account: Account,
        amount: Decimal,
    ) -> None:
        """
        Safely transfers cash between two accounts.

        Steps:
        1. Ensures cash accounts exist for both branches.
        2. Validates sufficient balance in source account.
        3. Deducts from source and adds to destination atomically.
        4. Logs all operations.
        """

        # Convert amount once to Decimal for precision
        amount = Decimal(amount)

        # Get or create cash accounts
        source_cash_account = CashAccountService.get_or_create_cash_account(
            company=cash_transfer.company,
            branch=source_account.branch,
        ).account
        destination_cash_account = CashAccountService.get_or_create_cash_account(
            company=cash_transfer.company,
            branch=destination_account.branch,
        ).account

        # Check for sufficient balance
        if source_cash_account.balance < amount:
            raise ValueError(
                f"Insufficient balance in source account (ID: {source_cash_account.pk}) "
                f"| Available: {source_cash_account.balance} | Requested: {amount}"
            )

        # Adjust balances atomically
        source_cash_account.balance -= amount
        source_cash_account.save(update_fields=["balance"])
        logger.info(
            f"Deducted amount '{amount}' from Source Account '{source_cash_account.pk}' "
            f"| New balance: {source_cash_account.balance}"
        )

        destination_cash_account.balance += amount
        destination_cash_account.save(update_fields=["balance"])
        
        logger.info(
            f"Added amount '{amount}' to Destination Account '{destination_cash_account.pk}' "
            f"| New balance: {destination_cash_account.balance}"
        )

        return
