from django.db import models
from django.db.models import Q
from transactions.models.transaction_model import Transaction
from company.models.company_model import Company
from branch.models.branch_model import Branch
from accounts.models.account_model import Account
from customers.models.customer_model import Customer
from suppliers.models.supplier_model import Supplier
from accounts.services.account_service import AccountsService
from rest_framework.response import Response
from loguru import logger
from decimal import Decimal
from django.db import transaction as db_transaction
from config.pagination.pagination import StandardResultsSetPagination

class TransactionService:
    @staticmethod
    def validate_transaction(transaction):
        logger.info(transaction)
        logger.debug(f"Validating transaction {transaction.transaction_number}")
        if transaction.total_amount <= 0:
            raise ValueError("Transaction amount must be greater than zero.")
        if transaction.debit_account == transaction.credit_account:
            raise ValueError("Debit and credit accounts cannot be the same.")
        if transaction.debit_account.is_frozen or transaction.credit_account.is_frozen:
            raise ValueError("Cannot apply transaction: one of the accounts is frozen.")
        logger.debug(f"Transaction {transaction.transaction_number} passed validation")
        
    def create_transaction(
                    company: Company,
                    branch: Branch,
                    debit_account: Account,
                    credit_account: Account,
                    transaction_type: str,
                    transaction_category: str,
                    total_amount: Decimal,
                    customer: Customer = None,
                    supplier: Supplier = None
                ):
        """
        Create a transaction with auto-generated transaction_number, status, and date.
        """
        try:
            transaction = Transaction.objects.create(
                company=company,
                branch=branch,
                debit_account=debit_account,
                credit_account=credit_account,
                transaction_type=transaction_type,
                transaction_category=transaction_category,
                customer=customer,
                supplier=supplier,
                total_amount = total_amount
                # total_amount defaults to 0
                # status defaults to 'DRAFT'
                # transaction_number is auto-generated in save()
                # transaction_date is auto_now_add
            )
            logger.info(f"Transaction {transaction.transaction_number} created with status {transaction.status}")
            return transaction
        except Exception as e:
            logger.exception(f"Error creating transaction: {str(e)}")
            raise
        
    @staticmethod
    @db_transaction.atomic
    def apply_transaction_to_accounts(transaction):
        """
        Docstring for apply_transaction_to_accounts
        
        :param transaction: Description

        """
        logger.info(f"Applying transaction {transaction.transaction_number}")
        TransactionService.validate_transaction(transaction)
        try:
            # account retrieval with select_for_update to prevent race (row locking)
            debit_account = Account.objects.select_for_update().get(id=transaction.debit_account.id)
            credit_account = Account.objects.select_for_update().get(id=transaction.credit_account.id)

            amount = transaction.total_amount

            debit_balance = AccountsService.get_account_balance(debit_account)
            logger.info(f'debit_bal:{debit_balance} + amount:{amount}')
            debit_account.balance = Decimal(debit_balance) + amount
            debit_account.save(update_fields=['balance'])
            logger.info(f"Debited Account {debit_account.id}: {debit_balance} → {debit_account.balance}")

            credit_balance = AccountsService.get_account_balance(credit_account)
            logger.info(f'debit_bal:{credit_balance} + amount:{amount}')
            credit_account.balance = Decimal(credit_balance) - amount
            credit_account.save(update_fields=['balance'])
            logger.info(f"Credited Account {credit_account.id}: {credit_balance} → {credit_account.balance}")

             # Mark transaction as completed
            transaction.status = "COMPLETED"
            transaction.save(update_fields=["status"])
            logger.info(f"Transaction {transaction.transaction_number} marked as COMPLETED")


        except Exception as e:
            transaction.status = "FAILED"
            transaction.save(update_fields=["status"])
            logger.exception(f"Transaction {transaction.transaction_number} failed: {e}, transaction status {transaction.status}")
            raise
    
    @staticmethod
    @db_transaction.atomic
    def reverse_transaction(transaction):
        logger.info(f"Reversing transaction {transaction.transaction_number}")
        try:
            debit_account = Account.objects.select_for_update().get(id=transaction.debit_account.id) # row locked for update
            credit_account = Account.objects.select_for_update().get(id=transaction.credit_account.id) # row locked for update                       
            amount = transaction.total_amount

            debit_balance = AccountsService.get_account_balance(debit_account)
            debit_account.balance = debit_balance - amount
            debit_account.save(update_fields=['balance'])
            logger.info(f"Reversed Debit Account {debit_account.id}: {debit_balance} → {debit_account.balance}")

            credit_balance = AccountsService.get_account_balance(credit_account)
            credit_account.balance = credit_balance + amount
            credit_account.save(update_fields=['balance'])
            logger.info(f"Reversed Credit Account {credit_account.id}: {credit_balance} → {credit_account.balance}")

        except Exception as e:
            logger.error(f"Transaction reversal {transaction.transaction_number} failed: {e}")
            raise
    

    @staticmethod
    @db_transaction.atomic
    def transfer_funds(from_account, to_account, amount):
        logger.info(f"Transferring {amount} from Account {from_account.id} to Account {to_account.id}")
        try:
            # Lock the accounts in a consistent order to avoid deadlocks
            if from_account.id < to_account.id:
                first, second = from_account, to_account
            else:
                first, second = to_account, from_account

            first = Account.objects.select_for_update().get(id=first.id)
            second = Account.objects.select_for_update().get(id=second.id)

            # After locking, determine which is which
            if first.id == from_account.id:
                from_account, to_account = first, second
            else:
                from_account, to_account = second, first

            # Check balance
            from_account_balance = AccountsService.get_account_balance(from_account)
            if from_account_balance < amount:
                raise ValueError("Insufficient funds in the source account.")

            # Update balances
            from_account.balance = from_account_balance - amount
            from_account.save(update_fields=['balance'])
            logger.info(f"Debited {amount} from Account {from_account.id}: {from_account_balance} → {from_account.balance}")

            to_account_balance = AccountsService.get_account_balance(to_account)
            to_account.balance = to_account_balance + amount
            to_account.save(update_fields=['balance'])
            logger.info(f"Credited {amount} to Account {to_account.id}: {to_account_balance} → {to_account.balance}")

        except Exception as e:
            logger.error(f"Fund transfer failed: {e}")
            raise

    @staticmethod
    def get_transaction_summary(transaction):
        logger.debug(f"Generating summary for transaction {transaction.transaction_number}")
        summary = {
            'transaction_number': transaction.transaction_number,
            'transaction_type': transaction.transaction_type,
            'transaction_category': transaction.transaction_category,
            'transaction_date': transaction.transaction_date,
            'total_amount': transaction.total_amount,
            'debit_account': {
                'id': transaction.debit_account.id,
                'name': transaction.debit_account.name,
            },
            'credit_account': {
                'id': transaction.credit_account.id,
                'name': transaction.credit_account.name,
            },
        }
        logger.debug(f"Transaction summary generated for {transaction.transaction_number}")
        return summary
    
    @staticmethod
    @db_transaction.atomic
    def delete_transaction(transaction):
        try:
            transaction_number = transaction.transaction_number
            transaction.delete()
            logger.info(f"Transaction {transaction_number} deleted successfully")
        except Exception as e:
            logger.error(f"Failed to delete transaction {transaction.transaction_number}: {e}")
            raise
    
    @staticmethod
    def list_transactions_by_account(account):
        logger.info(f"Listing transactions for Account {account.id}")
        transactions = Transaction.objects.filter(
            models.Q(debit_account=account) | models.Q(credit_account=account)
        ).order_by('-transaction_date')
        logger.info(f"Found {transactions.count()} transactions for Account {account.id}")
        return transactions
    
    @staticmethod
    def get_transactions_by_date_range(start_date, end_date):
        logger.info(f"Retrieving transactions from {start_date} to {end_date}")
        transactions = Transaction.objects.filter(
            transaction_date__range=(start_date, end_date)
        ).order_by('-transaction_date')
        logger.info(f"Found {transactions.count()} transactions in date range")
        return transactions
    
    @staticmethod
    def get_transactions_by_type(transaction_type, company, branch):
        logger.info(f"Retrieving transactions of type {transaction_type}")
        transactions = Transaction.objects.filter(
            company=company,
            branch=branch,
            transaction_type=transaction_type
        ).order_by('-transaction_date')
        logger.info(f"Found {transactions.count()} transactions of type {transaction_type}")
        return transactions
    
    @staticmethod
    def get_transactions_by_category(transaction_category, company, branch):
        logger.info(f"Retrieving transactions of category {transaction_category} for company {company.id}, branch {branch.id}")

        transactions = Transaction.objects.filter(
            transaction_category=transaction_category,
            company=company,
            branch=branch
        ).order_by('-transaction_date')

        logger.info(f"Found {transactions.count()} transactions of category {transaction_category} for company {company.id}, branch {branch.id}")

        return transactions

    
    @staticmethod
    def get_transactions_by_company(company):
        logger.info(f"Retrieving transactions for company {company.id}")
        transactions = Transaction.objects.filter(
            company=company
        ).order_by('-transaction_date')
        logger.info(f"Found {transactions.count()} transactions for company {company.id}")
        return transactions
    
    @staticmethod
    def get_transaction_by_branch(company, branch):
        logger.info(f"Retrieving transactions for branch {branch.id}")
        transactions = Transaction.objects.filter(
            company=company,
            branch=branch
        ).order_by('-transaction_date')
        logger.info(f"Found {transactions.count()} transactions for branch {branch.id}")
        return transactions

    @staticmethod
    def get_transactions(account=None, company=None):
        """
        Returns a filtered queryset of transactions.
        Pagination is handled in the view.
        """
        logger.info(f"Fetching transactions for account={account} company={company}")
        qs = Transaction.objects.all()
        if account:
            qs = qs.filter(models.Q(debit_account=account) | models.Q(credit_account=account))
        if company:
            qs = qs.filter(company=company)
        return qs.order_by('-transaction_date')

    
    @staticmethod
    def search_transactions(query):
        logger.info(f"Searching transactions with query '{query}'")
        transactions = Transaction.objects.filter(
            models.Q(transaction_number__icontains=query) |
            models.Q(debit_account__name__icontains=query) |
            models.Q(credit_account__name__icontains=query)
        ).order_by('-transaction_date')
        logger.info(f"Found {transactions.count()} transactions matching query '{query}'")
        return transactions
    
    @staticmethod
    def check_duplicate(transaction: Transaction):
        """
         checks duplicate transactions
        """
        transaction_number = transaction.transaction_number

        exists = Transaction.objects.filter(transaction_number=transaction_number).exists()

        if exists:
            logger.warning(f"Duplicate transaction number found: {transaction_number}")
            raise ValueError(f"Duplicate transaction number: {transaction_number}")
    
    @staticmethod
    def schedule_transaction(transaction_data, schedule_date):
        logger.info(f"Scheduling transaction for {schedule_date}")
        # Add to ScheduledTransaction model (you should create it)

    @staticmethod
    def get_account_ledger(account):
        return Transaction.objects.filter(
            Q(debit_account=account) | Q(credit_account=account)
        ).order_by("transaction_date")
    


    @staticmethod
    def get_opening_balance(account, date):
        debit_sum = Transaction.objects.filter(
            debit_account=account,
            transaction_date__lt=date
        ).aggregate(models.Sum('total_amount'))['total_amount__sum'] or 0

        credit_sum = Transaction.objects.filter(
            credit_account=account,
            transaction_date__lt=date
        ).aggregate(models.Sum('total_amount'))['total_amount__sum'] or 0

        return debit_sum - credit_sum
    
    @staticmethod
    def mark_transaction_pending(transaction):
        transaction.status = "PENDING"
        transaction.save(update_fields=["status"])

    @staticmethod
    def approve_transaction(transaction):
        transaction.status = "APPROVED"
        transaction.save(update_fields=["status"])
        TransactionService.apply_transaction_to_accounts(transaction)

    
    @staticmethod
    def enforce_transaction_limit(user, amount, daily_limit=10000):
        today_total = Transaction.objects.filter(
            created_by=user,
            transaction_date__date=models.functions.Now().date()
        ).aggregate(models.Sum("total_amount"))["total_amount__sum"] or 0

        if today_total + amount > daily_limit:
            raise ValueError("Daily transaction limit exceeded.")
        

    @staticmethod
    def export_transactions_to_csv(transactions):
        # return CSV file path or response
        pass


    
    @staticmethod
    def reconcile_account(account):
        calculated = (
            Transaction.objects.filter(debit_account=account)
            .aggregate(models.Sum("total_amount"))["total_amount__sum"] or 0
        ) - (
            Transaction.objects.filter(credit_account=account)
            .aggregate(models.Sum("total_amount"))["total_amount__sum"] or 0
        )

        if calculated != account.balance:
            logger.warning(
                f"Reconciliation mismatch for Account {account.id}: stored={account.balance}, calculated={calculated}"
            )
            return False

        return True





