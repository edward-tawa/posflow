from django.db import models, transaction as db_transaction
from django.db.models import Q
from accounts.models.account_model import Account
from transactions.models.transaction_model import Transaction
from loguru import logger

from django.db.models import Sum

class AccountsService:
    """
    Service class for account-related operations.
    """

    @staticmethod
    def get_account_balance(account: Account) -> float:
        logger.debug(f"Getting balance for Account {account.id}")
        balance = float(account.balance)
        logger.debug(f"Balance for Account {account.id}: {balance}")
        return balance
    
    @staticmethod
    @db_transaction.atomic
    def update_account_balance(account: Account, amount: float, is_debit: bool):
        logger.info(f"{'Debiting' if is_debit else 'Crediting'} Account {account.id} by {amount}")
        if is_debit:
            account.balance += amount
        else:
            account.balance -= amount
        account.save(update_fields=['balance'])
        logger.info(f"New balance for Account {account.id}: {account.balance}")

    @staticmethod
    def get_total_balance_by_type(account_type: str) -> float:
        logger.info(f"Calculating total balance for accounts of type '{account_type}'")
        total = Account.objects.filter(account_type=account_type).aggregate(
            total_balance=Sum('balance')
        )['total_balance'] or 0.0
        logger.info(f"Total balance for type '{account_type}': {total}")
        return float(total)
    
    @staticmethod
    def delete_account(account: Account):
        logger.info(f"Deleting Account {account.id}")
        account.delete()
        logger.info(f"Account {account.id} deleted successfully")

    @staticmethod
    def create_account(**data):
        logger.info(f"Creating account with data: {data}")
        account = Account.objects.create(**data)
        logger.info(f"Account {account.id} created successfully")
        return account
    
    @staticmethod
    def get_account_by_id(account_id: int) -> Account:
        logger.debug(f"Fetching account by ID: {account_id}")
        try:
            account = Account.objects.get(id=account_id)
            logger.debug(f"Account {account_id} retrieved")
            return account
        except Account.DoesNotExist:
            logger.warning(f"Account {account_id} does not exist")
            return None
        
    @staticmethod
    def update_account(account: Account, **data):
        logger.info(f"Updating Account {account.id} with data: {data}")
        for field, value in data.items():
            setattr(account, field, value)
        account.save()
        logger.info(f"Account {account.id} updated successfully")
        return account

    @staticmethod
    def list_accounts_by_type(account_type: str):
        logger.info(f"Listing accounts of type '{account_type}'")
        accounts = Account.objects.filter(account_type=account_type)
        logger.info(f"Found {accounts.count()} accounts of type '{account_type}'")
        return accounts
    
    @staticmethod
    def account_exists(account_id: int) -> bool:
        exists = Account.objects.filter(id=account_id).exists()
        logger.debug(f"Account {account_id} exists: {exists}")
        return exists
    
    @staticmethod
    def get_accounts_with_min_balance(min_balance: float):
        logger.info(f"Getting accounts with minimum balance of {min_balance}")
        accounts = Account.objects.filter(balance__gte=min_balance)
        logger.info(f"Found {accounts.count()} accounts with balance >= {min_balance}")
        return accounts
    
    @staticmethod
    def get_account_transactions(account: Account):
        logger.info(f"Retrieving transactions for Account {account.id}")
        transactions = Transaction.objects.filter(
            Q(debit_account=account) | Q(credit_account=account)
        ).order_by('-transaction_date')
        logger.info(f"Found {transactions.count()} transactions for Account {account.id}")
        return transactions
    

    @staticmethod
    def get_branch_account_transactions(account: Account, branch_id: int):
        transactions = Transaction.objects.filter(
            (Q(debit_account=account) | Q(credit_account=account)) &
            Q(branch_id=branch_id)
        ).order_by('-transaction_date')
        logger.info(f"Found {transactions.count()} transactions for Account {account.id} in Branch {branch_id}")
        return transactions
    
    
    @staticmethod
    def freeze_account(account: Account):
        account.is_frozen = True
        try:
            account.save(update_fields=['is_frozen'])
            logger.info(f"Account {account.id} frozen successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to freeze Account {account.id}: {e}")
            raise Exception(f"Could not freeze account {account.id}: {e}")
    
    @staticmethod
    def unfreeze_account(account: Account):
        account.is_frozen = False
        try:
            account.save(update_fields=['is_frozen'])
            logger.info(f"Account {account.id} unfrozen successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to unfreeze Account {account.id}: {e}")
            raise Exception(f"Could not unfreeze account {account.id}: {e}")

