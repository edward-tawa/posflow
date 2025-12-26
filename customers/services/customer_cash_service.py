from django.db import transaction as db_transaction
from django.db import models
from decimal import Decimal
from loguru import logger
from accounts.models import Account
from customers.models.customer_model import Customer
from accounts.models.sales_account_model import SalesAccount
from accounts.models.customer_account_model import CustomerAccount
from accounts.models.cash_account_model import CashAccount
from accounts.models.bank_account_model import BankAccount
from transactions.models.transaction_model import Transaction
from transactions.services.transaction_service import TransactionService


class CustomerCashService:


    @staticmethod
    @db_transaction.atomic
    def create_cash_sale(customer, amount, request):
        """
        Record a cash sale for a customer.
        Debit: Cash account
        Credit: Sales account
        """
        try:
            customer_account = None
            sales_account = None

            try:
                # Get customer and sales accounts
                customer_account = CustomerAccount.objects.get(customer=customer)
            except CustomerAccount.DoesNotExist:
                account_data = Account.objects.get(account_type = 'CUSTOMER')
                customer_account = CustomerAccount.objects.create(
                    customer = customer,
                    account = account_data,
                    branch = customer.branch,
                )
            logger.info(customer_account)

            try:
                sales_account = SalesAccount.objects.get(sales_person = request)
            except SalesAccount.DoesNotExist:
                account_data = Account.objects.get(account_type = 'SALE')
                sales_account = SalesAccount.objects.create(
                    account = account_data,
                    company = customer_account.account.company,
                    branch = customer_account.branch,
                    sales_person = request
                )
            logger.info(sales_account)

            # Get company's cash account for the branch
            cash_account = CashAccount.objects.get(
                account__company=customer_account.account.company,
                branch=customer_account.account.branch
            )

            # Define debit and credit accounts
            debit_account = cash_account.account  # Cash account
            credit_account = sales_account.account  # Sales account

            # Create transaction
            transaction = TransactionService.create_transaction(
                company=debit_account.company,
                branch=debit_account.branch,
                debit_account=debit_account,
                credit_account=credit_account,
                transaction_type="INCOMING",  # Cash received
                transaction_category="CASH SALE",
                customer=customer,
                supplier=None,
                total_amount=amount
            )

            # Apply transaction to accounts
            TransactionService.apply_transaction_to_accounts(transaction)

            logger.info(
                f"Cash sale recorded for Customer {customer.id} "
                f"({customer.first_name}), amount: {amount}"
            )

        except (CustomerAccount.DoesNotExist, SalesAccount.DoesNotExist, CashAccount.DoesNotExist) as e:
            logger.exception(
                f"Account missing for Customer {customer.id} ({customer.first_name}): {str(e)}"
            )
            raise

        except Exception as e:
            logger.exception(
                f"Error recording cash sale for Customer {customer.id} "
                f"({customer.first_name}), amount: {amount}: {str(e)}"
            )
            raise