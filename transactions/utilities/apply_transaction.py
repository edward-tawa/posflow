from accounts.services.accounts_service import AccountsService
from loguru import logger
from django.db import transaction as db_transaction

@db_transaction.atomic
def apply_transaction_to_accounts(transaction):
    try:
        debit_account = transaction.debit_account
        credit_account = transaction.credit_account
        amount = transaction.total_amount

        if amount <= 0:
            raise ValueError("Transaction amount must be greater than zero.")
        if debit_account == credit_account:
            raise ValueError("Debit and credit accounts cannot be the same.")

        # Update debit account
        debit_balance = AccountsService.get_account_balance(debit_account)
        debit_account.balance = debit_balance + amount
        debit_account.save(update_fields=['balance'])
        logger.info(f"Debited Account {debit_account.id}: {debit_balance} → {debit_account.balance}")

        # Update credit account
        credit_balance = AccountsService.get_account_balance(credit_account)
        credit_account.balance = credit_balance - amount
        credit_account.save(update_fields=['balance'])
        logger.info(f"Credited Account {credit_account.id}: {credit_balance} → {credit_account.balance}")

    except Exception as e:
        logger.error(f"Transaction failed: {e}")
        raise
