from typing import List
from django.db import transaction as db_transaction
from django.db.models.query import QuerySet
from loguru import logger
from branch.models.branch_model import Branch
from company.models.company_model import Company
from accounts.models.cash_account_model import CashAccount
from accounts.services.account_service import AccountsService


class CashAccountService:
    """
    Service class for cash account-related operations.
    """

    @staticmethod
    @db_transaction.atomic
    def create_cash_account(company: Company, branch: Branch, initial_balance: float = 0.0) -> CashAccount:
        """
        Create a new cash account and its associated account.
        """
        try:
            account = AccountsService.create_account(
                name=f"Cash Account - {branch.name}",
                company=company,
                account_type='CASH'
            )
            cash_account = CashAccount.objects.create(
                account=account,
                branch=branch,
                balance=initial_balance
            )
            logger.info(f"Cash Account for branch '{branch.name}' created for company '{company.name}'.")
            return cash_account
        except Exception as e:
            logger.error(f"Error creating cash account for branch '{branch.name}': {str(e)}")
            raise
    

    @staticmethod
    @db_transaction.atomic
    def get_or_create_cash_account(company: Company, branch: Branch) -> CashAccount:
        """
        Retrieve the cash account for a branch.
        Create it if it does not exist.
        """
        cash_account = CashAccount.objects.select_related(
            'account', 'account__company'
        ).filter(
            account__company=company,
            branch=branch
        ).first()

        if cash_account:
            return cash_account

        logger.info(
            f"No Cash Account found for branch '{branch.name}'. Creating one."
        )
        return CashAccountService.create_cash_account(
            company=company,
            branch=branch,
            initial_balance=0
        )


    @staticmethod
    @db_transaction.atomic
    def update_cash_account(cash_account: CashAccount, **kwargs) -> CashAccount:
        """
        Update an existing cash account.
        """
        for key, value in kwargs.items():
            setattr(cash_account, key, value)
        cash_account.save()
        logger.info(f"Cash Account for branch '{cash_account.branch.name}' updated with {kwargs}.")
        return cash_account

    @staticmethod
    @db_transaction.atomic
    def delete_cash_account(cash_account: CashAccount) -> None:
        """
        Delete an existing cash account.
        """
        cash_account_id = cash_account.id
        cash_account.delete()
        logger.info(f"Cash Account with id '{cash_account_id}' deleted.")

    @staticmethod
    def get_cash_account_by_id(cash_account_id: int) -> CashAccount | None:
        """
        Retrieve a cash account by its ID.
        """
        try:
            return CashAccount.objects.select_related('branch', 'account', 'account__company').get(id=cash_account_id)
        except CashAccount.DoesNotExist:
            logger.warning(f"Cash Account with id '{cash_account_id}' not found.")
            return None

    @staticmethod
    def get_cash_accounts_by_company(company: Company) -> QuerySet[CashAccount]:
        """
        Retrieve all cash accounts for a given company.
        """
        qs = CashAccount.objects.filter(account__company=company)\
            .select_related('branch', 'account')
        if not qs.exists():
            logger.warning(f"No cash accounts found for company '{company.name}'.")
        return qs

    @staticmethod
    def get_cash_accounts_by_branch(branch: Branch) -> QuerySet[CashAccount]:
        """
        Retrieve all cash accounts for a given branch.
        """
        qs = CashAccount.objects.filter(branch=branch)\
            .select_related('account', 'account__company')
        if not qs.exists():
            logger.warning(f"No cash accounts found for branch '{branch.name}'.")
        return qs

    @staticmethod
    def get_cash_account_balance(cash_account: CashAccount) -> float:
        """
        Retrieve the balance of a cash account.
        """
        return cash_account.balance

    @staticmethod
    def search_cash_accounts(company: Company, query: str) -> QuerySet[CashAccount]:
        """
        Search cash accounts by branch name for a given company.
        """
        qs = CashAccount.objects.filter(
            account__company=company,
            branch__name__icontains=query
        ).select_related('branch', 'account')
        if not qs.exists():
            logger.warning(f"No cash accounts found for query '{query}' in company '{company.name}'.")
        return qs