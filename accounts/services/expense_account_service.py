from django.db import transaction as db_transaction
from django.db.models import Q
from django.db.models.query import QuerySet
from loguru import logger
from branch.models.branch_model import Branch
from company.models.company_model import Company
from accounts.models.expense_account_model import ExpenseAccount
from accounts.services.account_service import AccountsService


class ExpenseAccountService:
    """
    Service class for expense account-related operations.
    """

    @staticmethod
    @db_transaction.atomic
    def create_expense_account(company: Company, branch: Branch, expense_name: str) -> ExpenseAccount:
        try:
            account = AccountsService.create_account(
                name=f"Expense Account - {expense_name}",
                company=company,
                account_type='EXPENSE'
            )
            expense_account = ExpenseAccount.objects.create(
                account=account,
                branch=branch,
                expense_name=expense_name
            )
            logger.info(f"Expense Account for '{expense_name}' created for company '{company.name}'.")
            return expense_account
        except Exception as e:
            logger.error(f"Error creating expense account for '{expense_name}': {str(e)}")
            raise

    
    @staticmethod
    @db_transaction.atomic
    def get_or_create_expense_account(company: Company, branch: Branch, expense_name: str) -> ExpenseAccount:
        """
        Retrieve the expense account for a branch and expense name.
        Create it if it does not exist.
        """
        expense_account = ExpenseAccount.objects.select_related(
            'account', 'account__company'
        ).filter(
            account__company=company,
            branch=branch,
            expense_name=expense_name
        ).first()

        if expense_account:
            return expense_account

        logger.info(
            f"No Expense Account found for expense '{expense_name}' in branch '{branch.name}'. Creating one."
        )
        return ExpenseAccountService.create_expense_account(
            company=company,
            branch=branch,
            expense_name=expense_name
        )
    

    @staticmethod
    @db_transaction.atomic
    def update_expense_account(expense_account: ExpenseAccount, **kwargs) -> ExpenseAccount:
        for key, value in kwargs.items():
            setattr(expense_account, key, value)
        expense_account.save()
        logger.info(f"Expense Account for '{expense_account.expense_name}' updated with {kwargs}.")
        return expense_account

    @staticmethod
    @db_transaction.atomic
    def delete_expense_account(expense_account: ExpenseAccount) -> None:
        expense_account_id = expense_account.id
        expense_account.delete()
        logger.info(f"Expense Account with id '{expense_account_id}' deleted.")

    @staticmethod
    def get_expense_account_by_id(expense_account_id: int) -> ExpenseAccount | None:
        try:
            return ExpenseAccount.objects.select_related(
                'branch', 'account', 'account__company'
            ).get(id=expense_account_id)
        except ExpenseAccount.DoesNotExist:
            logger.warning(f"Expense Account with id '{expense_account_id}' not found.")
            return None

    @staticmethod
    def get_expense_accounts_by_branch(branch: Branch) -> QuerySet[ExpenseAccount]:
        qs = ExpenseAccount.objects.filter(branch=branch).select_related('branch', 'account', 'account__company')
        if not qs.exists():
            logger.warning(f"No expense accounts found for branch '{branch.name}'.")
        return qs

    @staticmethod
    def get_expense_accounts_by_company(company: Company) -> QuerySet[ExpenseAccount]:
        qs = ExpenseAccount.objects.filter(account__company=company).select_related('branch', 'account')
        if not qs.exists():
            logger.warning(f"No expense accounts found for company '{company.name}'.")
        return qs

    @staticmethod
    def get_expense_account_balance(expense_account: ExpenseAccount) -> float:
        balance = AccountsService.get_account_balance(expense_account.account)
        logger.info(f"Balance for Expense Account '{expense_account.expense_name}': {balance}")
        return balance

    @staticmethod
    def search_expense_accounts(company: Company, query: str) -> QuerySet[ExpenseAccount]:
        """
        Search expense accounts by expense name OR branch name for a given company.
        """
        qs = ExpenseAccount.objects.filter(
            Q(account__company=company) &
            (Q(expense_name__icontains=query) | Q(branch__name__icontains=query))
        ).select_related('branch', 'account')

        if not qs.exists():
            logger.warning(f"No expense accounts found for query '{query}' in company '{company.name}'.")
        return qs

    @staticmethod
    def filter_expense_accounts_by_balance(company: Company, min_balance: float = None, max_balance: float = None) -> QuerySet[ExpenseAccount]:
        """
        Filter expense accounts by balance range. If min_balance or max_balance is None, ignore that bound.
        """
        qs = ExpenseAccount.objects.filter(account__company=company).select_related('branch', 'account')
        filtered_ids = []

        for ea in qs:
            balance = AccountsService.get_account_balance(ea.account)
            if (min_balance is None or balance >= min_balance) and (max_balance is None or balance <= max_balance):
                filtered_ids.append(ea.id)

        if not filtered_ids:
            logger.warning(f"No expense accounts found in balance range '{min_balance}' - '{max_balance}' for company '{company.name}'.")

        return ExpenseAccount.objects.filter(id__in=filtered_ids).select_related('branch', 'account')

    @staticmethod
    def get_all_expense_accounts() -> QuerySet[ExpenseAccount]:
        return ExpenseAccount.objects.select_related('branch', 'account', 'account__company').all()
