from accounts.models.purchases_returns_account_model import PurchasesReturnsAccount
from django.db import transaction as db_transaction
from loguru import logger
from django.db.models.query import QuerySet
from django.db.models import Q
from branch.models.branch_model import Branch
from company.models.company_model import Company
from accounts.services.account_service import AccountsService


class PurchasesReturnsService:
    """
    Service class for purchases returns account-related operations.
    """

    @staticmethod
    @db_transaction.atomic
    def create_purchases_returns_account(company: Company, branch: Branch, supplier_name: str) -> PurchasesReturnsAccount:
        """
        Create a new purchases returns account and its associated account.
        """
        try:
            account = AccountsService.create_account(
                name=f"Purchases Returns Account - {supplier_name}",
                company=company,
                account_type='PURCHASES_RETURNS'
            )
            purchases_returns_account = PurchasesReturnsAccount.objects.create(
                account=account,
                branch=branch,
                supplier_name=supplier_name
            )
            logger.info(f"Purchases Returns Account for '{supplier_name}' created for company '{company.name}'.")
            return purchases_returns_account
        except Exception as e:
            logger.error(f"Error creating purchases returns account for '{supplier_name}': {str(e)}")
            raise

    
    @staticmethod
    @db_transaction.atomic
    def get_or_create_purchases_returns_account(company: Company, branch: Branch, supplier_name: str) -> PurchasesReturnsAccount:
        """
        Retrieve the purchases returns account for a branch and supplier name.
        Create it if it does not exist.
        """
        purchases_returns_account = PurchasesReturnsAccount.objects.select_related(
            'account', 'account__company'
        ).filter(
            account__company=company,
            branch=branch,
            supplier_name=supplier_name
        ).first()

        if purchases_returns_account:
            return purchases_returns_account

        logger.info(
            f"No Purchases Returns Account found for supplier '{supplier_name}' in branch '{branch.name}'. Creating one."
        )
        return PurchasesReturnsService.create_purchases_returns_account(
            company=company,
            branch=branch,
            supplier_name=supplier_name
        )

    @staticmethod
    @db_transaction.atomic
    def update_purchases_returns_account(purchases_returns_account: PurchasesReturnsAccount, **kwargs) -> PurchasesReturnsAccount:
        """
        Update an existing purchases returns account.
        """
        for key, value in kwargs.items():
            setattr(purchases_returns_account, key, value)
        purchases_returns_account.save()
        logger.info(f"Purchases Returns Account for '{purchases_returns_account.supplier_name}' updated with {kwargs}.")
        return purchases_returns_account

    @staticmethod
    @db_transaction.atomic
    def delete_purchases_returns_account(purchases_returns_account: PurchasesReturnsAccount) -> None:
        """
        Delete an existing purchases returns account.
        """
        account_id = purchases_returns_account.id
        purchases_returns_account.delete()
        logger.info(f"Purchases Returns Account with id '{account_id}' deleted.")

    @staticmethod
    def get_purchases_returns_account_by_id(account_id: int) -> PurchasesReturnsAccount | None:
        """
        Retrieve a purchases returns account by its ID.
        """
        try:
            return PurchasesReturnsAccount.objects.select_related(
                'branch', 'account', 'account__company'
            ).get(id=account_id)
        except PurchasesReturnsAccount.DoesNotExist:
            logger.warning(f"Purchases Returns Account with id '{account_id}' not found.")
            return None

    @staticmethod
    def get_purchases_returns_accounts_by_branch(branch: Branch) -> QuerySet[PurchasesReturnsAccount]:
        """
        Retrieve all purchases returns accounts for a given branch.
        """
        qs = PurchasesReturnsAccount.objects.filter(branch=branch).select_related('branch', 'account', 'account__company')
        if not qs.exists():
            logger.warning(f"No purchases returns accounts found for branch '{branch.name}'.")
        return qs

    @staticmethod
    def get_purchases_returns_accounts_by_company(company: Company) -> QuerySet[PurchasesReturnsAccount]:
        """
        Retrieve all purchases returns accounts for a given company.
        """
        qs = PurchasesReturnsAccount.objects.filter(account__company=company).select_related('branch', 'account')
        if not qs.exists():
            logger.warning(f"No purchases returns accounts found for company '{company.name}'.")
        return qs

    @staticmethod
    def get_purchases_returns_account_balance(account: PurchasesReturnsAccount) -> float:
        """
        Retrieve the balance of a purchases returns account.
        """
        balance = AccountsService.get_account_balance(account.account)
        logger.info(f"Balance for Purchases Returns Account '{account.supplier_name}': {balance}")
        return balance

    @staticmethod
    def search_purchases_returns_accounts(company: Company, query: str) -> QuerySet[PurchasesReturnsAccount]:
        """
        Search purchases returns accounts by supplier name OR branch name for a given company.
        """
        qs = PurchasesReturnsAccount.objects.filter(
            Q(account__company=company) &
            (Q(supplier_name__icontains=query) | Q(branch__name__icontains=query))
        ).select_related('branch', 'account')

        if not qs.exists():
            logger.warning(f"No purchases returns accounts found for query '{query}' in company '{company.name}'.")
        return qs

    @staticmethod
    def filter_purchases_returns_accounts_by_balance(company: Company, min_balance: float = None, max_balance: float = None) -> QuerySet[PurchasesReturnsAccount]:
        """
        Filter purchases returns accounts by balance range.
        """
        qs = PurchasesReturnsAccount.objects.filter(account__company=company).select_related('branch', 'account')
        filtered_ids = [
            pra.id for pra in qs
            if (min_balance is None or AccountsService.get_account_balance(pra.account) >= min_balance) and
               (max_balance is None or AccountsService.get_account_balance(pra.account) <= max_balance)
        ]

        if not filtered_ids:
            logger.warning(f"No purchases returns accounts found in balance range '{min_balance}' - '{max_balance}' for company '{company.name}'.")

        return PurchasesReturnsAccount.objects.filter(id__in=filtered_ids).select_related('branch', 'account')

    @staticmethod
    def get_purchases_returns_accounts_by_supplier_name(company: Company, supplier_name: str) -> QuerySet[PurchasesReturnsAccount]:
        """
        Retrieve purchases returns accounts by supplier name for a given company.
        """
        qs = PurchasesReturnsAccount.objects.filter(account__company=company, supplier_name__icontains=supplier_name).select_related('branch', 'account')
        if not qs.exists():
            logger.warning(f"No purchases returns accounts found for supplier '{supplier_name}' in company '{company.name}'.")
        return qs
