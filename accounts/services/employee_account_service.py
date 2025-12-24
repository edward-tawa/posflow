from typing import List
from django.db import transaction as db_transaction
from django.db.models import Q, F
from django.db.models.query import QuerySet
from loguru import logger
from branch.models.branch_model import Branch
from company.models.company_model import Company
from accounts.models.employee_account_model import EmployeeAccount
from accounts.services.account_service import AccountsService


class EmployeeAccountService:
    """
    Service class for employee account-related operations.
    """

    @staticmethod
    @db_transaction.atomic
    def create_employee_account(company: Company, branch: Branch, employee_name: str) -> EmployeeAccount:
        try:
            account = AccountsService.create_account(
                name=f"Employee Account - {employee_name}",
                company=company,
                account_type='EMPLOYEE'
            )
            employee_account = EmployeeAccount.objects.create(
                account=account,
                branch=branch,
                employee_name=employee_name
            )
            logger.info(f"Employee Account for '{employee_name}' created for company '{company.name}'.")
            return employee_account
        except Exception as e:
            logger.error(f"Error creating employee account for '{employee_name}': {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def get_or_create_employee_account(company: Company, branch: Branch, employee_name: str) -> EmployeeAccount:
        """
        Retrieve the employee account for a branch and employee name.
        Create it if it does not exist.
        """
        employee_account = EmployeeAccount.objects.select_related(
            'account', 'account__company'
        ).filter(
            account__company=company,
            branch=branch,
            employee_name=employee_name
        ).first()

        if employee_account:
            return employee_account

        logger.info(
            f"No Employee Account found for employee '{employee_name}' in branch '{branch.name}'. Creating one."
        )
        return EmployeeAccountService.create_employee_account(
            company=company,
            branch=branch,
            employee_name=employee_name
        )

    @staticmethod
    @db_transaction.atomic
    def update_employee_account(employee_account: EmployeeAccount, **kwargs) -> EmployeeAccount:
        for key, value in kwargs.items():
            setattr(employee_account, key, value)
        employee_account.save()
        logger.info(f"Employee Account for '{employee_account.employee_name}' updated with {kwargs}.")
        return employee_account

    @staticmethod
    @db_transaction.atomic
    def delete_employee_account(employee_account: EmployeeAccount) -> None:
        employee_account_id = employee_account.id
        employee_account.delete()
        logger.info(f"Employee Account with id '{employee_account_id}' deleted.")

    @staticmethod
    def get_employee_account_by_id(employee_account_id: int) -> EmployeeAccount | None:
        try:
            return EmployeeAccount.objects.select_related(
                'branch', 'account', 'account__company'
            ).get(id=employee_account_id)
        except EmployeeAccount.DoesNotExist:
            logger.warning(f"Employee Account with id '{employee_account_id}' not found.")
            return None

    @staticmethod
    def get_employee_accounts_by_branch(branch: Branch) -> QuerySet[EmployeeAccount]:
        qs = EmployeeAccount.objects.filter(branch=branch).select_related('account', 'account__company')
        if not qs.exists():
            logger.warning(f"No employee accounts found for branch '{branch.name}'.")
        return qs

    @staticmethod
    def get_employee_accounts_by_company(company: Company) -> QuerySet[EmployeeAccount]:
        qs = EmployeeAccount.objects.filter(account__company=company).select_related('branch', 'account')
        if not qs.exists():
            logger.warning(f"No employee accounts found for company '{company.name}'.")
        return qs

    @staticmethod
    def get_employee_account_balance(employee_account: EmployeeAccount) -> float:
        balance = AccountsService.get_account_balance(employee_account.account)
        logger.info(f"Balance for Employee Account '{employee_account.employee_name}': {balance}")
        return balance

    @staticmethod
    def search_employee_accounts(company: Company, query: str) -> QuerySet[EmployeeAccount]:
        """
        Search employee accounts by name or branch for a company.
        """
        qs = EmployeeAccount.objects.filter(
            Q(account__company=company) &
            (Q(employee_name__icontains=query) | Q(branch__name__icontains=query))
        ).select_related('branch', 'account')
        if not qs.exists():
            logger.warning(f"No employee accounts found for query '{query}' in company '{company.name}'.")
        return qs

    @staticmethod
    def filter_employee_accounts_by_balance(company: Company, min_balance: float = None, max_balance: float = None) -> QuerySet[EmployeeAccount]:
        """
        Filter employee accounts by balance range. If min_balance or max_balance is None, ignore that bound.
        """
        qs = EmployeeAccount.objects.filter(account__company=company).select_related('branch', 'account')
        filtered_ids = []

        for ea in qs:
            balance = AccountsService.get_account_balance(ea.account)
            if (min_balance is None or balance >= min_balance) and (max_balance is None or balance <= max_balance):
                filtered_ids.append(ea.id)

        if not filtered_ids:
            logger.warning(f"No employee accounts found in balance range '{min_balance}' - '{max_balance}' for company '{company.name}'.")

        return EmployeeAccount.objects.filter(id__in=filtered_ids).select_related('branch', 'account')

    @staticmethod
    def get_employee_accounts_with_negative_balance(company: Company) -> QuerySet[EmployeeAccount]:
        return EmployeeAccountService.filter_employee_accounts_by_balance(company, max_balance=-0.01)

    @staticmethod
    def get_employee_accounts_with_positive_balance(company: Company) -> QuerySet[EmployeeAccount]:
        return EmployeeAccountService.filter_employee_accounts_by_balance(company, min_balance=0.01)

    @staticmethod
    def get_all_employee_accounts() -> QuerySet[EmployeeAccount]:
        return EmployeeAccount.objects.select_related('branch', 'account', 'account__company').all()
