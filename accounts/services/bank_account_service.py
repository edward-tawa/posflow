from accounts.models.account_model import Account
from accounts.services.account_service import AccountsService
from accounts.models.bank_account_model import BankAccount
from django.db import transaction as db_transaction
from loguru import logger
from typing import List, Dict
from branch.models.branch_model import Branch
from company.models.company_model import Company




class BankAccountService:
    """
    Service class for bank account-related operations.
    """

    @staticmethod
    @db_transaction.atomic
    def create_bank_account(company: Company, branch: Branch, bank_name: str) -> BankAccount:
        """
        Create a new bank account and its associated account.

        :param name: Name of the bank account
        :param company: Company to which the bank account belongs
        :param bank_name: Name of the bank
        :param branch: Branch associated with the bank account (optional)
        :return: Created BankAccount instance
        """
        try:
            # Create the associated Account first
            account = AccountsService.create_account(
                name=f"{bank_name} Account",
                company=company,
                account_type='BANK'
            )
            # Now create the BankAccount
            bank_account = BankAccount.objects.create(
                account=account,
                bank_name=bank_name,
                branch=branch
            )
            logger.info(f"Bank Account '{bank_account.bank_name}' created for company '{company.name}'.")
            return bank_account
        except Exception as e:
            logger.error(f"Error creating bank account: {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def get_or_create_bank_account(company: Company, branch: Branch, bank_name: str) -> BankAccount:
        """
        Retrieve the bank account for a branch and bank name.
        Create it if it does not exist.
        """
        bank_account = BankAccount.objects.select_related(
            'account', 'account__company'
        ).filter(
            account__company=company,
            branch=branch,
            bank_name=bank_name
        ).first()

        if bank_account:
            return bank_account

        logger.info(
            f"No Bank Account found for bank '{bank_name}' in branch '{branch.name}'. Creating one."
        )
        return BankAccountService.create_bank_account(
            company=company,
            branch=branch,
            bank_name=bank_name
        )

    @staticmethod
    @db_transaction.atomic
    def update_bank_account(bank_account: BankAccount, **kwargs) -> BankAccount:
        """
        Update an existing bank account.

        :param bank_account: BankAccount instance to update
        :param kwargs: Fields to update
        :return: Updated BankAccount instance
        """
        try:
            for key, value in kwargs.items():
                setattr(bank_account, key, value)
            bank_account.save(update_fields=kwargs.keys())
            logger.info(f"Bank Account '{bank_account.bank_name}' updated.")
            return bank_account
        except Exception as e:
            logger.error(f"Error updating bank account '{bank_account.bank_name}': {str(e)}")
            raise

    

    @staticmethod
    @db_transaction.atomic
    def delete_bank_account(bank_account: BankAccount) -> None:
        """
        Delete a bank account.

        :param bank_account: BankAccount instance to delete
        """
        try:
            bank_account_id = bank_account.id
            bank_account.delete()
            logger.info(f"Bank Account '{bank_account_id}' deleted.")
        except Exception as e:
            logger.error(f"Error deleting bank account '{bank_account.id}': {str(e)}")
            raise
    

    @staticmethod
    def get_bank_account_by_id(bank_account_id: int) -> BankAccount | None:
        """
        Retrieve a bank account by its ID.

        :param bank_account_id: ID of the BankAccount
        :return: BankAccount instance or None if not found
        """
        try:
            return BankAccount.objects.get(id=bank_account_id)
        except BankAccount.DoesNotExist:
            logger.warning(f"Bank Account with id {bank_account_id} not found.")
            return None
        
    
    @staticmethod
    def get_bank_accounts_by_company(company: Company):
        """
        Retrieve all bank accounts for a given company.

        :param company: Company instance
        :return: QuerySet of BankAccount instances
        """
        return BankAccount.objects.filter(account__company=company)
    

    @staticmethod
    def get_bank_account_balance(bank_account: BankAccount) -> float:
        """
        Get the balance of a bank account.

        :param bank_account: BankAccount instance
        :return: Balance as a float
        """
        balance = AccountsService.get_account_balance(bank_account.account)
        logger.info(f"Balance for Bank Account '{bank_account.bank_name}': {balance}")
        return balance

    @staticmethod
    def get_bank_accounts_by_branch(branch: Branch):
        return BankAccount.objects.filter(branch=branch)
    

    @staticmethod
    def search_bank_accounts(company: Company, query: str):
        return BankAccount.objects.filter(account__company=company, bank_name__icontains=query)
    

    @staticmethod
    @db_transaction.atomic
    def create_bank_accounts_bulk(company: Company, branch: Branch, banks: List[Dict[str, str]]) -> List[BankAccount]:
        """
        Bulk create bank accounts using AccountsService.bulk_create_accounts for parent Account creation.
        """
        if not banks:
            return []

        # Step 1: Prepare data for parent Accounts
        accounts_data = [
            {
                "name": f"{bank['bank_name']} Account",
                "company": company,
                "branch": branch,
                "account_type": "BANK"
            }
            for bank in banks
        ]

        # Step 2: Bulk create parent Accounts using AccountsService
        created_accounts = AccountsService.bulk_create_accounts(accounts_data)

        # Map account name to object for child creation
        name_to_account = {acct.name: acct for acct in created_accounts}

        # Step 3: Prepare BankAccount objects
        bank_account_objs = [
            BankAccount(
                account=name_to_account[f"{bank['bank_name']} Account"],
                bank_name=bank['bank_name'],
                branch=branch
            )
            for bank in banks
        ]

        # Step 4: Bulk create BankAccounts
        BankAccount.objects.bulk_create(bank_account_objs)

        logger.info(f"Created {len(bank_account_objs)} bank accounts for company '{company.name}'")
        return bank_account_objs

