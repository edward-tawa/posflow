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
from transactions.services.transaction_service import TransactionService



class TransactionQueryService:

    @staticmethod
    def get_transactions_by_account(account):
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
    def get_transactions_by_id(company, branch, id: int):
        transactions = Transaction.objects.filter(
            company=company,
            branch=branch,
            id=id,
        ).order_by('-transaction_date')
        logger.info(f"Found {transactions.count()} transactions for id {id} in branch {branch.id}")
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
        logger.info(f"No duplicate found for transaction number: {transaction_number}")
    
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