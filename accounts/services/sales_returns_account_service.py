from accounts.models.sales_returns_account_model import SalesReturnsAccount
from branch.models.branch_model import Branch
from company.models.company_model import Company
from accounts.services.account_service import AccountsService
from loguru import logger
from django.db import transaction as db_transaction
from django.db.models.query import QuerySet
from django.db.models import Q


class SalesReturnsAccountService:
    """
    Service class for sales returns account-related operations.
    """

    @staticmethod
    @db_transaction.atomic
    def create_sales_returns_account(company: Company, branch: Branch, customer_name: str) -> SalesReturnsAccount:
        """
        Create a new sales returns account and its associated account.
        """
        try:
            account = AccountsService.create_account(
                name=f"Sales Returns Account - {customer_name}",
                company=company,
                account_type='SALES_RETURNS'
            )
            sales_returns_account = SalesReturnsAccount.objects.create(
                account=account,
                branch=branch,
                customer_name=customer_name
            )
            logger.info(f"Sales Returns Account for '{customer_name}' created for company '{company.name}'.")
            return sales_returns_account
        except Exception as e:
            logger.error(f"Error creating sales returns account for '{customer_name}': {str(e)}")
            raise

    
    @staticmethod
    @db_transaction.atomic
    def get_or_create_sales_returns_account(company: Company, branch: Branch, customer_name: str) -> SalesReturnsAccount:
        """
        Retrieve the sales returns account for a branch and customer name.
        Create it if it does not exist.
        """
        sales_returns_account = SalesReturnsAccount.objects.select_related(
            'account', 'account__company'
        ).filter(
            account__company=company,
            branch=branch,
            customer_name=customer_name
        ).first()

        if sales_returns_account:
            return sales_returns_account

        logger.info(
            f"No Sales Returns Account found for customer '{customer_name}' in branch '{branch.name}'. Creating one."
        )
        return SalesReturnsService.create_sales_returns_account(
            company=company,
            branch=branch,
            customer_name=customer_name
        )

    @staticmethod
    @db_transaction.atomic
    def update_sales_returns_account(account: SalesReturnsAccount, **kwargs) -> SalesReturnsAccount:
        """
        Update an existing sales returns account.
        """
        for key, value in kwargs.items():
            setattr(account, key, value)
        account.save()
        logger.info(f"Sales Returns Account for '{account.customer_name}' updated with {kwargs}.")
        return account

    @staticmethod
    @db_transaction.atomic
    def delete_sales_returns_account(account: SalesReturnsAccount) -> None:
        """
        Delete an existing sales returns account.
        """
        account_id = account.id
        account.delete()
        logger.info(f"Sales Returns Account with id '{account_id}' deleted.")

    @staticmethod
    def get_sales_returns_account_by_id(account_id: int) -> SalesReturnsAccount | None:
        """
        Retrieve a sales returns account by its ID.
        """
        try:
            return SalesReturnsAccount.objects.select_related(
                'branch', 'account', 'account__company'
            ).get(id=account_id)
        except SalesReturnsAccount.DoesNotExist:
            logger.warning(f"Sales Returns Account with id '{account_id}' not found.")
            return None

    @staticmethod
    def get_sales_returns_accounts_by_branch(branch: Branch) -> QuerySet[SalesReturnsAccount]:
        """
        Retrieve all sales returns accounts for a given branch.
        """
        qs = SalesReturnsAccount.objects.filter(branch=branch).select_related('branch', 'account', 'account__company')
        if not qs.exists():
            logger.warning(f"No sales returns accounts found for branch '{branch.name}'.")
        return qs

    @staticmethod
    def get_sales_returns_accounts_by_company(company: Company) -> QuerySet[SalesReturnsAccount]:
        """
        Retrieve all sales returns accounts for a given company.
        """
        qs = SalesReturnsAccount.objects.filter(account__company=company).select_related('branch', 'account')
        if not qs.exists():
            logger.warning(f"No sales returns accounts found for company '{company.name}'.")
        return qs

    @staticmethod
    def get_sales_returns_account_balance(account: SalesReturnsAccount) -> float:
        """
        Retrieve the balance of a sales returns account.
        """
        balance = AccountsService.get_account_balance(account.account)
        logger.info(f"Balance for Sales Returns Account '{account.customer_name}': {balance}")
        return balance

    @staticmethod
    def search_sales_returns_accounts(company: Company, query: str) -> QuerySet[SalesReturnsAccount]:
        """
        Search sales returns accounts by customer name or branch name for a given company.
        """
        qs = SalesReturnsAccount.objects.filter(
            Q(account__company=company) &
            (Q(customer_name__icontains=query) | Q(branch__name__icontains=query))
        ).select_related('branch', 'account')

        if not qs.exists():
            logger.warning(f"No sales returns accounts found for query '{query}' in company '{company.name}'.")
        return qs

    @staticmethod
    def filter_sales_returns_accounts_by_balance(
        company: Company,
        min_balance: float = None,
        max_balance: float = None
    ) -> QuerySet[SalesReturnsAccount]:
        """
        Filter sales returns accounts by balance range.
        """
        qs = SalesReturnsAccount.objects.filter(account__company=company).select_related('branch', 'account')
        filtered_ids = [
            sa.id for sa in qs
            if (min_balance is None or AccountsService.get_account_balance(sa.account) >= min_balance)
            and (max_balance is None or AccountsService.get_account_balance(sa.account) <= max_balance)
        ]

        if not filtered_ids:
            logger.warning(f"No sales returns accounts found in balance range '{min_balance}' - '{max_balance}' for company '{company.name}'.")

        return SalesReturnsAccount.objects.filter(id__in=filtered_ids).select_related('branch', 'account')

    @staticmethod
    def get_sales_returns_accounts_by_customer_name(company: Company, customer_name: str) -> QuerySet[SalesReturnsAccount]:
        """
        Retrieve sales returns accounts by customer name for a given company.
        """
        qs = SalesReturnsAccount.objects.filter(
            account__company=company,
            customer_name__icontains=customer_name
        ).select_related('branch', 'account')

        if not qs.exists():
            logger.warning(f"No sales returns accounts found for customer name '{customer_name}' in company '{company.name}'.")
        return qs
