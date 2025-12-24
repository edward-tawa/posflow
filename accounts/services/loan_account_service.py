from django.db import transaction as db_transaction
from django.db.models import Q
from django.db.models.query import QuerySet
from loguru import logger
from branch.models.branch_model import Branch
from company.models.company_model import Company
from accounts.models.loan_account_model import LoanAccount
from accounts.services.account_service import AccountsService


class LoanAccountService:
    """
    Service class for loan account-related operations.
    """

    @staticmethod
    @db_transaction.atomic
    def create_loan_account(company: Company, branch: Branch, borrower_name: str, loan_amount: float) -> LoanAccount:
        try:
            account = AccountsService.create_account(
                name=f"Loan Account - {borrower_name}",
                company=company,
                account_type='LOAN'
            )
            loan_account = LoanAccount.objects.create(
                account=account,
                branch=branch,
                borrower_name=borrower_name,
                loan_amount=loan_amount
            )
            logger.info(f"Loan Account for '{borrower_name}' created for company '{company.name}'.")
            return loan_account
        except Exception as e:
            logger.error(f"Error creating loan account for '{borrower_name}': {str(e)}")
            raise
    
    @staticmethod
    @db_transaction.atomic
    def get_or_create_loan_account(company: Company, branch: Branch, borrower_name: str, loan_amount: float) -> LoanAccount:
        """
        Retrieve the loan account for a branch and borrower name.
        Create it if it does not exist.
        """
        loan_account = LoanAccount.objects.select_related(
            'account', 'account__company'
        ).filter(
            account__company=company,
            branch=branch,
            borrower_name=borrower_name
        ).first()

        if loan_account:
            return loan_account

        logger.info(
            f"No Loan Account found for borrower '{borrower_name}' in branch '{branch.name}'. Creating one."
        )
        return LoanAccountService.create_loan_account(
            company=company,
            branch=branch,
            borrower_name=borrower_name,
            loan_amount=loan_amount
        )

    @staticmethod
    @db_transaction.atomic
    def update_loan_account(loan_account: LoanAccount, **kwargs) -> LoanAccount:
        for key, value in kwargs.items():
            setattr(loan_account, key, value)
        loan_account.save()
        logger.info(f"Loan Account for '{loan_account.borrower_name}' updated with {kwargs}.")
        return loan_account

    @staticmethod
    @db_transaction.atomic
    def delete_loan_account(loan_account: LoanAccount) -> None:
        loan_account_id = loan_account.id
        loan_account.delete()
        logger.info(f"Loan Account with id '{loan_account_id}' deleted.")

    @staticmethod
    def get_loan_account_by_id(loan_account_id: int) -> LoanAccount | None:
        try:
            return LoanAccount.objects.select_related('branch', 'account', 'account__company').get(id=loan_account_id)
        except LoanAccount.DoesNotExist:
            logger.warning(f"Loan Account with id '{loan_account_id}' not found.")
            return None

    @staticmethod
    def get_loan_accounts_by_branch(branch: Branch) -> QuerySet[LoanAccount]:
        qs = LoanAccount.objects.filter(branch=branch).select_related('branch', 'account', 'account__company')
        if not qs.exists():
            logger.warning(f"No loan accounts found for branch '{branch.name}'.")
        return qs

    @staticmethod
    def get_loan_accounts_by_company(company: Company) -> QuerySet[LoanAccount]:
        qs = LoanAccount.objects.filter(account__company=company).select_related('branch', 'account')
        if not qs.exists():
            logger.warning(f"No loan accounts found for company '{company.name}'.")
        return qs

    @staticmethod
    def get_loan_account_balance(loan_account: LoanAccount) -> float:
        balance = AccountsService.get_account_balance(loan_account.account)
        logger.info(f"Balance for Loan Account '{loan_account.borrower_name}': {balance}")
        return balance

    @staticmethod
    def search_loan_accounts(company: Company, query: str) -> QuerySet[LoanAccount]:
        qs = LoanAccount.objects.filter(
            Q(account__company=company) &
            (Q(borrower_name__icontains=query) | Q(branch__name__icontains=query))
        ).select_related('branch', 'account')
        if not qs.exists():
            logger.warning(f"No loan accounts found for query '{query}' in company '{company.name}'.")
        return qs

    @staticmethod
    def filter_loan_accounts_by_balance(company: Company, min_balance: float = None, max_balance: float = None) -> QuerySet[LoanAccount]:
        qs = LoanAccount.objects.filter(account__company=company).select_related('branch', 'account')
        filtered_ids = [
            la.id for la in qs
            if (min_balance is None or AccountsService.get_account_balance(la.account) >= min_balance)
            and (max_balance is None or AccountsService.get_account_balance(la.account) <= max_balance)
        ]
        if not filtered_ids:
            logger.warning(f"No loan accounts found in balance range '{min_balance}' - '{max_balance}' for company '{company.name}'.")
        return LoanAccount.objects.filter(id__in=filtered_ids).select_related('branch', 'account')

    @staticmethod
    def get_loan_accounts_due_for_payment(company: Company, due_date) -> QuerySet[LoanAccount]:
        qs = LoanAccount.objects.filter(account__company=company, due_date__lte=due_date).select_related('branch', 'account')
        if not qs.exists():
            logger.warning(f"No loan accounts due for payment by '{due_date}' in company '{company.name}'.")
        return qs

    @staticmethod
    def get_loan_accounts_overdue(company: Company, current_date) -> QuerySet[LoanAccount]:
        qs = LoanAccount.objects.filter(account__company=company, due_date__lt=current_date).select_related('branch', 'account')
        overdue_ids = [la.id for la in qs if AccountsService.get_account_balance(la.account) > 0]
        if not overdue_ids:
            logger.warning(f"No overdue loan accounts as of '{current_date}' in company '{company.name}'.")
        return LoanAccount.objects.filter(id__in=overdue_ids).select_related('branch', 'account')

    @staticmethod
    def get_loan_accounts_by_borrower_name(company: Company, borrower_name: str) -> QuerySet[LoanAccount]:
        qs = LoanAccount.objects.filter(account__company=company, borrower_name__icontains=borrower_name).select_related('branch', 'account')
        if not qs.exists():
            logger.warning(f"No loan accounts found for borrower '{borrower_name}' in company '{company.name}'.")
        return qs

    @staticmethod
    def get_loan_accounts_by_amount_range(company: Company, min_amount: float = None, max_amount: float = None) -> QuerySet[LoanAccount]:
        qs = LoanAccount.objects.filter(account__company=company).select_related('branch', 'account')
        filtered_ids = [la.id for la in qs if (min_amount is None or la.loan_amount >= min_amount) and (max_amount is None or la.loan_amount <= max_amount)]
        if not filtered_ids:
            logger.warning(f"No loan accounts found in amount range '{min_amount}' - '{max_amount}' for company '{company.name}'.")
        return LoanAccount.objects.filter(id__in=filtered_ids).select_related('branch', 'account')

    @staticmethod
    def get_loan_accounts_with_no_payments_made(company: Company) -> QuerySet[LoanAccount]:
        qs = LoanAccount.objects.filter(account__company=company, payments_made=0).select_related('branch', 'account')
        if not qs.exists():
            logger.warning(f"No loan accounts with no payments made found for company '{company.name}'.")
        return qs

    @staticmethod
    def get_all_loan_accounts() -> QuerySet[LoanAccount]:
        return LoanAccount.objects.select_related('branch', 'account', 'account__company').all()
