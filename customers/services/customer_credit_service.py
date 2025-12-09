from django.db import transaction as db_transaction
from django.db import models
from loguru import logger
from customers.models.customer_model import Customer
from accounts.models.customer_account import CustomerAccount
from transactions.models.transaction_model import Transaction
from transactions.services.transcation_service import TransactionService


class CustomerCreditService:

    @staticmethod
    @db_transaction.atomic
    def apply_credit(transaction):
        """
        Apply credit to a customer's account.
        """

        TransactionService.apply_transaction_to_accounts(transaction)
        
        

increase_credit_limit(customer, amount)

reduce_credit_limit(customer, amount)

get_customer_outstanding_balance(customer)

record_payment(customer, amount, method)

validate_credit_limit(customer, amount)