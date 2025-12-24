from accounts.models.supplier_account_model import SupplierAccount
from django.db import transaction as db_transaction
from loguru import logger
from django.db.models.query import QuerySet
from django.db.models import Q
from branch.models.branch_model import Branch
from company.models.company_model import Company
from accounts.services.account_service import AccountsService


class SupplierAccountService:
    """
    Service class for supplier account-related operations.
    """

    @staticmethod
    @db_transaction.atomic
    def create_supplier_account(company: Company, branch: Branch, supplier_name: str) -> SupplierAccount:
        """
        Create a new supplier account and its associated account.
        """
        try:
            account = AccountsService.create_account(
                name=f"Supplier Account - {supplier_name}",
                company=company,
                account_type='SUPPLIER'
            )
            supplier_account = SupplierAccount.objects.create(
                account=account,
                branch=branch,
                supplier_name=supplier_name
            )
            logger.info(f"Supplier Account for '{supplier_name}' created for company '{company.name}'.")
            return supplier_account
        except Exception as e:
            logger.error(f"Error creating supplier account for '{supplier_name}': {str(e)}")
            raise


    @staticmethod
    @db_transaction.atomic
    def get_or_create_supplier_account(company: Company, branch: Branch, supplier_name: str) -> SupplierAccount:
        """
        Retrieve the supplier account for a branch and supplier name.
        Create it if it does not exist.
        """
        supplier_account = SupplierAccount.objects.select_related(
            'account', 'account__company'
        ).filter(
            account__company=company,
            branch=branch,
            supplier_name=supplier_name
        ).first()

        if supplier_account:
            return supplier_account

        logger.info(
            f"No Supplier Account found for supplier '{supplier_name}' in branch '{branch.name}'. Creating one."
        )
        return SupplierAccountService.create_supplier_account(
            company=company,
            branch=branch,
            supplier_name=supplier_name
        )

    @staticmethod
    @db_transaction.atomic
    def update_supplier_account(account: SupplierAccount, **kwargs) -> SupplierAccount:
        """
        Update an existing supplier account.
        """
        for key, value in kwargs.items():
            setattr(account, key, value)
        account.save()
        logger.info(f"Supplier Account for '{account.supplier_name}' updated with {kwargs}.")
        return account

    @staticmethod
    @db_transaction.atomic
    def delete_supplier_account(account: SupplierAccount) -> None:
        """
        Delete an existing supplier account.
        """
        account_id = account.id
        account.delete()
        logger.info(f"Supplier Account with id '{account_id}' deleted.")

    @staticmethod
    def get_supplier_account_by_id(account_id: int) -> SupplierAccount | None:
        """
        Retrieve a supplier account by its ID.
        """
        try:
            return SupplierAccount.objects.select_related('branch', 'account', 'account__company').get(id=account_id)
        except SupplierAccount.DoesNotExist:
            logger.warning(f"Supplier Account with id '{account_id}' not found.")
            return None

    @staticmethod
    def get_supplier_accounts_by_branch(branch: Branch) -> QuerySet[SupplierAccount]:
        """
        Retrieve all supplier accounts for a given branch.
        """
        qs = SupplierAccount.objects.filter(branch=branch).select_related('branch', 'account', 'account__company')
        if not qs.exists():
            logger.warning(f"No supplier accounts found for branch '{branch.name}'.")
        return qs

    @staticmethod
    def get_supplier_accounts_by_company(company: Company) -> QuerySet[SupplierAccount]:
        """
        Retrieve all supplier accounts for a given company.
        """
        qs = SupplierAccount.objects.filter(account__company=company).select_related('branch', 'account')
        if not qs.exists():
            logger.warning(f"No supplier accounts found for company '{company.name}'.")
        return qs

    @staticmethod
    def get_supplier_account_balance(account: SupplierAccount) -> float:
        """
        Retrieve the balance of a supplier account.
        """
        balance = AccountsService.get_account_balance(account.account)
        logger.info(f"Balance for Supplier Account '{account.supplier_name}': {balance}")
        return balance

    @staticmethod
    def search_supplier_accounts(company: Company, query: str) -> QuerySet[SupplierAccount]:
        """
        Search supplier accounts by supplier name for a given company.
        """
        qs = SupplierAccount.objects.filter(
            account__company=company,
            supplier_name__icontains=query
        ).select_related('branch', 'account')

        if not qs.exists():
            logger.warning(f"No supplier accounts found for query '{query}' in company '{company.name}'.")
        return qs

    @staticmethod
    def filter_supplier_accounts_by_balance(
        company: Company,
        min_balance: float = None,
        max_balance: float = None
    ) -> QuerySet[SupplierAccount]:
        """
        Filter supplier accounts by balance range for a given company.
        """
        supplier_accounts = SupplierAccount.objects.filter(account__company=company).select_related('branch', 'account')
        filtered_ids = [
            account.id for account in supplier_accounts
            if (min_balance is None or AccountsService.get_account_balance(account.account) >= min_balance)
            and (max_balance is None or AccountsService.get_account_balance(account.account) <= max_balance)
        ]

        if not filtered_ids:
            logger.warning(f"No supplier accounts found with balance between {min_balance} and {max_balance} for company '{company.name}'.")

        return SupplierAccount.objects.filter(id__in=filtered_ids).select_related('branch', 'account')
