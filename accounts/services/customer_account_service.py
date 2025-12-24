from typing import List
from django.db import transaction as db_transaction
from django.db.models import Q
from django.db.models.query import QuerySet
from loguru import logger
from branch.models.branch_model import Branch
from company.models.company_model import Company
from accounts.models.customer_account_model import CustomerAccount
from accounts.services.account_service import AccountsService


class CustomerAccountService:
    """
    Service class for customer account-related operations.
    """

    @staticmethod
    @db_transaction.atomic
    def create_customer_account(company: Company, branch: Branch, customer_name: str) -> CustomerAccount:
        """
        Create a new customer account and its associated account.
        """
        try:
            account = AccountsService.create_account(
                name=f"Customer Account - {customer_name}",
                company=company,
                account_type='CUSTOMER'
            )
            customer_account = CustomerAccount.objects.create(
                account=account,
                branch=branch,
                customer_name=customer_name
            )
            logger.info(f"Customer Account for '{customer_name}' created for company '{company.name}'.")
            return customer_account
        except Exception as e:
            logger.error(f"Error creating customer account for '{customer_name}': {str(e)}")
            raise
    
    @staticmethod
    @db_transaction.atomic
    def get_or_create_customer_account(company: Company, branch: Branch, customer_name: str) -> CustomerAccount:
        """
        Retrieve the customer account for a branch and customer name.
        Create it if it does not exist.
        """
        customer_account = CustomerAccount.objects.select_related(
            'account', 'account__company'
        ).filter(
            account__company=company,
            branch=branch,
            customer_name=customer_name
        ).first()

        if customer_account:
            return customer_account

        logger.info(
            f"No Customer Account found for customer '{customer_name}' in branch '{branch.name}'. Creating one."
        )
        return CustomerAccountService.create_customer_account(
            company=company,
            branch=branch,
            customer_name=customer_name
        )

    @staticmethod
    @db_transaction.atomic
    def update_customer_account(customer_account: CustomerAccount, **kwargs) -> CustomerAccount:
        """
        Update an existing customer account.
        """
        for key, value in kwargs.items():
            setattr(customer_account, key, value)
        customer_account.save()
        logger.info(f"Customer Account for '{customer_account.customer_name}' updated with {kwargs}.")
        return customer_account

    @staticmethod
    @db_transaction.atomic
    def delete_customer_account(customer_account: CustomerAccount) -> None:
        """
        Delete an existing customer account.
        """
        customer_account_id = customer_account.id
        customer_account.delete()
        logger.info(f"Customer Account with id '{customer_account_id}' deleted.")

    @staticmethod
    def get_customer_account_by_id(customer_account_id: int) -> CustomerAccount | None:
        """
        Retrieve a customer account by its ID.
        """
        try:
            return CustomerAccount.objects.select_related(
                'branch', 'account', 'account__company'
            ).get(id=customer_account_id)
        except CustomerAccount.DoesNotExist:
            logger.warning(f"Customer Account with id '{customer_account_id}' not found.")
            return None

    @staticmethod
    def get_customer_accounts_by_branch(branch: Branch) -> QuerySet[CustomerAccount]:
        """
        Retrieve all customer accounts for a given branch.
        """
        qs = CustomerAccount.objects.filter(branch=branch)\
            .select_related('account', 'account__company')
        if not qs.exists():
            logger.warning(f"No customer accounts found for branch '{branch.name}'.")
        return qs

    @staticmethod
    def get_customer_accounts_by_company(company: Company) -> QuerySet[CustomerAccount]:
        """
        Retrieve all customer accounts for a given company.
        """
        qs = CustomerAccount.objects.filter(account__company=company)\
            .select_related('branch', 'account')
        if not qs.exists():
            logger.warning(f"No customer accounts found for company '{company.name}'.")
        return qs

    @staticmethod
    def search_customer_accounts(company: Company, query: str) -> QuerySet[CustomerAccount]:
        """
        Search customer accounts by customer name or branch name for a given company.
        """
        qs = CustomerAccount.objects.filter(
            Q(account__company=company) &
            (Q(customer_name__icontains=query) | Q(branch__name__icontains=query))
        ).select_related('branch', 'account')

        if not qs.exists():
            logger.warning(f"No customer accounts found for query '{query}' in company '{company.name}'.")
        return qs
