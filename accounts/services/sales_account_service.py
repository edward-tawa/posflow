from accounts.models.account_model import Account
from accounts.models.sales_account_model import SalesAccount
from django.db import transaction as db_transaction
from loguru import logger
from django.db.models.query import QuerySet
from django.db.models import Q
from branch.models.branch_model import Branch
from company.models.company_model import Company
from accounts.services.account_service import AccountsService



class SalesAccountService:
    """
    Service class for sales account-related operations.
    """

    @staticmethod
    @db_transaction.atomic
    def create_sales_account(company: Company, branch: Branch) -> SalesAccount:
        """
        Create a new sales account and its associated account.
        """
        try:
            account = AccountsService.create_account(
                company=company,
                account_type='SALES'
            )
            sales_account = SalesAccount.objects.create(
                account=account,
                company=company,
                branch=branch,
            )
            logger.info(f"Sales Account created for company '{company.name}'.")
            return sales_account
        except Exception as e:
            logger.error(f"Error creating sales account for company '{company.name}': {str(e)}")
            raise

    
    @staticmethod
    @db_transaction.atomic
    def get_or_create_sales_account(company: Company, branch: Branch) -> SalesAccount:
        """
        Retrieve the sales account for a branch and customer name.
        Create it if it does not exist.
        """
        sales_account = SalesAccount.objects.select_related(
            'account', 'account__company'
        ).filter(
            account__company=company,
            branch=branch,
        ).first()

        if sales_account:
            return sales_account

        logger.info(
            f"No Sales Account found in branch '{branch.name}'. Creating one."
        )
        return SalesAccountService.create_sales_account(
            company=company,
            branch=branch,
        )

    @staticmethod
    @db_transaction.atomic
    def update_sales_account(sales_account: SalesAccount, **kwargs) -> SalesAccount:
        """
        Update an existing sales account.
        """
        for key, value in kwargs.items():
            setattr(sales_account, key, value)
        sales_account.save()
        logger.info(f"Sales Account for '{sales_account.customer_name}' updated with {kwargs}.")
        return sales_account

    @staticmethod
    @db_transaction.atomic
    def delete_sales_account(sales_account: SalesAccount) -> None:
        """
        Delete an existing sales account.
        """
        account_id = sales_account.id
        sales_account.delete()
        logger.info(f"Sales Account with id '{account_id}' deleted.")

    @staticmethod
    def get_sales_account_by_id(account_id: int) -> SalesAccount | None:
        """
        Retrieve a sales account by its ID.
        """
        try:
            return SalesAccount.objects.select_related(
                'branch', 'account', 'account__company'
            ).get(id=account_id)
        except SalesAccount.DoesNotExist:
            logger.warning(f"Sales Account with id '{account_id}' not found.")
            return None

    @staticmethod
    def get_sales_accounts_by_branch(branch: Branch) -> QuerySet[SalesAccount]:
        """
        Retrieve all sales accounts for a specific branch.
        """
        qs = SalesAccount.objects.filter(branch=branch).select_related('branch', 'account', 'account__company')
        if not qs.exists():
            logger.warning(f"No sales accounts found for branch '{branch.name}'.")
        return qs

    @staticmethod
    def get_sales_accounts_by_company(company: Company) -> QuerySet[SalesAccount]:
        """
        Retrieve all sales accounts for a given company.
        """
        qs = SalesAccount.objects.filter(account__company=company).select_related('branch', 'account')
        if not qs.exists():
            logger.warning(f"No sales accounts found for company '{company.name}'.")
        return qs

    @staticmethod
    def get_sales_account_balance(sales_account: SalesAccount) -> float:
        """
        Retrieve the balance of a sales account.
        """
        balance = AccountsService.get_account_balance(sales_account.account)
        logger.info(f"Balance for Sales Account '{sales_account.customer_name}': {balance}")
        return balance

    @staticmethod
    def search_sales_accounts(company: Company, query: str) -> QuerySet[SalesAccount]:
        """
        Search sales accounts by customer name OR branch name for a given company.
        """
        qs = SalesAccount.objects.filter(
            Q(account__company=company) &
            (Q(customer_name__icontains=query) | Q(branch__name__icontains=query))
        ).select_related('branch', 'account')

        if not qs.exists():
            logger.warning(f"No sales accounts found for query '{query}' in company '{company.name}'.")
        return qs

    @staticmethod
    def filter_sales_accounts_by_balance(company: Company, min_balance: float = None, max_balance: float = None) -> QuerySet[SalesAccount]:
        """
        Filter sales accounts by balance range.
        """
        qs = SalesAccount.objects.filter(account__company=company).select_related('branch', 'account')
        filtered_ids = [
            sa.id for sa in qs
            if (min_balance is None or AccountsService.get_account_balance(sa.account) >= min_balance) and
               (max_balance is None or AccountsService.get_account_balance(sa.account) <= max_balance)
        ]

        if not filtered_ids:
            logger.warning(f"No sales accounts found in balance range '{min_balance}' - '{max_balance}' for company '{company.name}'.")

        return SalesAccount.objects.filter(id__in=filtered_ids).select_related('branch', 'account')

    @staticmethod
    def get_sales_accounts_with_balance_above(company: Company, threshold: float) -> QuerySet[SalesAccount]:
        """
        Retrieve all sales accounts with a balance above a certain threshold.
        """
        qs = SalesAccount.objects.filter(account__company=company).select_related('account')
        filtered_ids = [sa.id for sa in qs if AccountsService.get_account_balance(sa.account) > threshold]
        logger.info(f"Sales Accounts with balance above {threshold} for company '{company.name}': {len(filtered_ids)} found.")
        return SalesAccount.objects.filter(id__in=filtered_ids).select_related('branch', 'account')

    @staticmethod
    def get_sales_accounts_with_balance_below(company: Company, threshold: float) -> QuerySet[SalesAccount]:
        """
        Retrieve all sales accounts with a balance below a certain threshold.
        """
        qs = SalesAccount.objects.filter(account__company=company).select_related('account')
        filtered_ids = [sa.id for sa in qs if AccountsService.get_account_balance(sa.account) < threshold]
        logger.info(f"Sales Accounts with balance below {threshold} for company '{company.name}': {len(filtered_ids)} found.")
        return SalesAccount.objects.filter(id__in=filtered_ids).select_related('branch', 'account')
    


    
