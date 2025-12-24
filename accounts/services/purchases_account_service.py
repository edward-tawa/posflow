from accounts.models.purchases_account_model import PurchasesAccount
from django.db import transaction as db_transaction
from loguru import logger
from django.db.models.query import QuerySet
from django.db.models import Q
from branch.models.branch_model import Branch
from company.models.company_model import Company
from accounts.services.account_service import AccountsService


class PurchasesAccountService:
    """
    Service class for purchases account-related operations.
    """

    @staticmethod
    @db_transaction.atomic
    def create_purchases_account(company: Company, branch: Branch, supplier_name: str) -> PurchasesAccount:
        """
        Create a new purchases account and its associated account.
        """
        try:
            account = AccountsService.create_account(
                name=f"Purchases Account - {supplier_name}",
                company=company,
                account_type='PURCHASES'
            )
            purchases_account = PurchasesAccount.objects.create(
                account=account,
                branch=branch,
                supplier_name=supplier_name
            )
            logger.info(f"Purchases Account for '{supplier_name}' created for company '{company.name}'.")
            return purchases_account
        except Exception as e:
            logger.error(f"Error creating purchases account for '{supplier_name}': {str(e)}")
            raise
    
    

    @staticmethod
    @db_transaction.atomic
    def get_or_create_purchases_account(company: Company, branch: Branch, supplier_name: str) -> PurchasesAccount:
        """
        Retrieve the purchases account for a branch and supplier name.
        Create it if it does not exist.
        """
        purchases_account = PurchasesAccount.objects.select_related(
            'account', 'account__company'
        ).filter(
            account__company=company,
            branch=branch,
            supplier_name=supplier_name
        ).first()

        if purchases_account:
            return purchases_account

        logger.info(
            f"No Purchases Account found for supplier '{supplier_name}' in branch '{branch.name}'. Creating one."
        )
        return PurchasesAccountService.create_purchases_account(
            company=company,
            branch=branch,
            supplier_name=supplier_name
        )


    @staticmethod
    @db_transaction.atomic
    def update_purchases_account(purchases_account: PurchasesAccount, **kwargs) -> PurchasesAccount:
        """
        Update an existing purchases account.
        """
        for key, value in kwargs.items():
            setattr(purchases_account, key, value)
        purchases_account.save()
        logger.info(f"Purchases Account for '{purchases_account.supplier_name}' updated with {kwargs}.")
        return purchases_account

    @staticmethod
    @db_transaction.atomic
    def delete_purchases_account(purchases_account: PurchasesAccount) -> None:
        """
        Delete an existing purchases account.
        """
        purchases_account_id = purchases_account.id
        purchases_account.delete()
        logger.info(f"Purchases Account with id '{purchases_account_id}' deleted.")

    @staticmethod
    def get_purchases_account_by_id(purchases_account_id: int) -> PurchasesAccount | None:
        """
        Retrieve a purchases account by its ID.
        """
        try:
            return PurchasesAccount.objects.select_related(
                'branch', 'account', 'account__company'
            ).get(id=purchases_account_id)
        except PurchasesAccount.DoesNotExist:
            logger.warning(f"Purchases Account with id '{purchases_account_id}' not found.")
            return None

    @staticmethod
    def get_purchases_accounts_by_branch(branch: Branch) -> QuerySet[PurchasesAccount]:
        """
        Retrieve all purchases accounts for a given branch.
        """
        qs = PurchasesAccount.objects.filter(branch=branch).select_related('branch', 'account', 'account__company')
        if not qs.exists():
            logger.warning(f"No purchases accounts found for branch '{branch.name}'.")
        return qs

    @staticmethod
    def get_purchases_accounts_by_company(company: Company) -> QuerySet[PurchasesAccount]:
        """
        Retrieve all purchases accounts for a given company.
        """
        qs = PurchasesAccount.objects.filter(account__company=company).select_related('branch', 'account')
        if not qs.exists():
            logger.warning(f"No purchases accounts found for company '{company.name}'.")
        return qs

    @staticmethod
    def get_purchases_account_balance(purchases_account: PurchasesAccount) -> float:
        """
        Retrieve the balance of a purchases account.
        """
        balance = AccountsService.get_account_balance(purchases_account.account)
        logger.info(f"Balance for Purchases Account '{purchases_account.supplier_name}': {balance}")
        return balance

    @staticmethod
    def search_purchases_accounts(company: Company, query: str) -> QuerySet[PurchasesAccount]:
        """
        Search purchases accounts by supplier name OR branch name for a given company.
        """
        qs = PurchasesAccount.objects.filter(
            Q(account__company=company) &
            (Q(supplier_name__icontains=query) | Q(branch__name__icontains=query))
        ).select_related('branch', 'account')
        if not qs.exists():
            logger.warning(f"No purchases accounts found for query '{query}' in company '{company.name}'.")
        return qs

    @staticmethod
    def filter_purchases_accounts_by_balance(company: Company, min_balance: float = None, max_balance: float = None) -> QuerySet[PurchasesAccount]:
        """
        Filter purchases accounts by balance range. If min_balance or max_balance is None, ignore that bound.
        """
        qs = PurchasesAccount.objects.filter(account__company=company).select_related('branch', 'account')
        filtered_ids = []

        for pa in qs:
            balance = AccountsService.get_account_balance(pa.account)
            if (min_balance is None or balance >= min_balance) and (max_balance is None or balance <= max_balance):
                filtered_ids.append(pa.id)

        if not filtered_ids:
            logger.warning(f"No purchases accounts found in balance range '{min_balance}' - '{max_balance}' for company '{company.name}'.")

        return PurchasesAccount.objects.filter(id__in=filtered_ids).select_related('branch', 'account')
