from django.db import transaction as db_transaction
from django.db import models
from decimal import Decimal
from loguru import logger
from customers.models.customer_model import Customer
from accounts.models.sales_account_model import SalesAccount
from accounts.models.customer_account_model import CustomerAccount
from accounts.models.cash_account_model import CashAccount
from accounts.models.bank_account_model import BankAccount
from transactions.models.transaction_model import Transaction
from transactions.services.transaction_service import TransactionService


class CustomerCreditService:

    @staticmethod
    @db_transaction.atomic
    def create_credit_sale(customer, amount):
        """
        Apply credit to a customer's account.
        Debit: Customer account
        Credit: Sales account
        """
        try:
            customer_account = CustomerAccount.objects.get(customer=customer)
            sales_account = SalesAccount.objects.get(customer=customer)

            debit_account = customer_account.account
            credit_account = sales_account.account

            transaction = TransactionService.create_transaction(
                company=debit_account.company,
                branch=debit_account.branch,
                debit_account=debit_account,
                credit_account=credit_account,
                transaction_type="CREDIT",  # Ensure this exists in Transaction.TRANSACTION_TYPES
                transaction_category="CREDIT SALE",
                customer=customer,
                supplier=None,
                total_amount=amount
            )

            TransactionService.apply_transaction_to_accounts(transaction)
            logger.info(
                f"Credit sale applied for Customer {customer.id} "
                f"({customer.first_name}), amount: {amount}"
            )

        except (CustomerAccount.DoesNotExist, SalesAccount.DoesNotExist) as e:
            logger.exception(
                f"Account missing for Customer {customer.id} ({customer.first_name}): {str(e)}"
            )
            raise

        except Exception as e:
            logger.exception(
                f"Error applying credit for Customer {customer.id} "
                f"({customer.first_name}), amount: {amount}: {str(e)}"
            )
            raise


    
    
    @staticmethod
    @db_transaction.atomic
    def get_customer_outstanding_balance(customer):
        """
        Return the customer's outstanding balance.
        Negative balance indicates the customer owes money.
        Returns Decimal("0.00") if balance is zero or positive.
        """
        try:
            customer_account = CustomerAccount.objects.get(customer=customer)
            balance = customer_account.account.balance or Decimal("0.00")
            
            # Only negative balances indicate outstanding amount
            if balance >= 0:
                return Decimal("0.00")
            return balance

        except CustomerAccount.DoesNotExist as e:
            logger.exception(
                f"Error getting outstanding balance for Customer {customer.id} "
                f"({customer.first_name}): {str(e)}"
            )
            raise


    @staticmethod
    @db_transaction.atomic
    def record_customer_payment(customer, amount, payment_method="CASH"):
        """
        Record a payment made by the customer.
        """
        try:
            # Get the customer's account (OneToOneField)
            customer_account = CustomerAccount.objects.get(customer=customer)

            # Determine the debit account based on payment method
            if payment_method == "CASH":
                debit_account = CashAccount.objects.get(
                    account__company=customer.company,
                    account__branch=customer.branch
                ).account
            elif payment_method == "BANK":
                debit_account = BankAccount.objects.get(
                    account__company=customer.company,
                    account__branch=customer.branch
                ).account
            else:
                raise ValueError(f"Unsupported payment method: {payment_method}")

            credit_account = customer_account.account

            transaction = TransactionService.create_transaction(
                company=credit_account.company,
                branch=credit_account.branch,
                debit_account=debit_account,
                credit_account=credit_account,
                transaction_type="INCOMING",
                transaction_category="CUSTOMER PAYMENT",
                customer=customer,
                supplier=None,
                total_amount=amount,
                payment_method=payment_method
            )

            TransactionService.apply_transaction_to_accounts(transaction)
            logger.info(f"Payment of {amount} recorded for Customer {customer.id}")

        except CustomerAccount.DoesNotExist:
            logger.error(f"CustomerAccount not found for Customer {customer.id}")
            raise
        except (CashAccount.DoesNotExist, BankAccount.DoesNotExist) as e:
            logger.error(f"Payment account not found: {str(e)}")
            raise
        except Exception as e:
            logger.exception(
                f"Error recording payment for Customer {customer.id} "
                f"({customer.first_name}): {str(e)}"
            )
            raise
        

    @staticmethod
    @db_transaction.atomic
    def customer_refund(customer, transaction):
        """
        Process a refund to the customer by reversing the original transaction.
        Money should move FROM the company TO the customer's account.
        """
        try:
            # 1. Get customer's account
            customer_account = CustomerAccount.objects.get(customer=customer)
            customer_acc = customer_account.account

            # 2. Original transaction accounts
            original_debit = transaction.debit_account
            original_credit = transaction.credit_account
            total_amount = transaction.total_amount

            # 3. Build a reversing transaction
            # Refund direction:
            # Company → Customer
            new_transaction = TransactionService.create_transaction(
                company=customer_acc.company,
                branch=customer_acc.branch,
                debit_account=original_credit,    # company pays back (reverse)
                credit_account=original_debit,      # customer receives refund
                transaction_type="OUTGOING",
                transaction_category=transaction.transaction_category,
                customer=customer,
                supplier=None,
                total_amount=total_amount
            )

            # 4. Apply the refund transaction to the ledgers(accounts concerned)
            TransactionService.apply_transaction_to_accounts(new_transaction)

            logger.info(f"Refund of {total_amount} processed for Customer {customer.id}")

        except CustomerAccount.DoesNotExist:
            logger.error(f"CustomerAccount not found for Customer {customer.id}")
            raise

        except Exception as e:
            logger.exception(
                f"Error processing refund for Customer {customer.id}"
                f"({customer.first_name}): {str(e)}"
            )
            raise

    @staticmethod
    @db_transaction.atomic
    def get_customer_statement(customer, start_date, end_date):
        """
        Retrieve all transactions for a customer within a date range.
        """
        try:
            transactions = Transaction.objects.filter(
                customer=customer,
                transaction_date__range=(start_date, end_date)
            ).order_by('-transaction_date')

            return transactions

        except Exception as e:
            logger.exception(
                f"Error retrieving statement for Customer {customer.first_name}"
                f"({customer.first_name}): {str(e)}"
            )

    @staticmethod
    @db_transaction.atomic
    def create_customer_credit_limit(customer, limit_amount):
        """
        Set or update the credit limit for the customer.
        """
        try:
            if limit_amount < 0:
                raise ValueError("Credit limit cannot be negative.")

            customer_account = CustomerAccount.objects.get(customer=customer)
            old_limit = customer_account.credit_limit

            customer_account.credit_limit = limit_amount
            customer_account.save(update_fields=["credit_limit"])

            logger.info(
                f"Credit limit updated for Customer {customer.id} ({customer.first_name}): "
                f"{old_limit} -> {limit_amount}"
            )

            return customer_account

        except CustomerAccount.DoesNotExist as e:
            logger.error(
                f"CustomerAccount not found for Customer {customer.id} ({customer.first_name})"
            )
            raise

        except Exception as e:
            logger.exception(
                f"Unexpected error setting credit limit for Customer {customer.id} "
                f"({customer.first_name}): {str(e)}"
            )
            raise

    @staticmethod
    @db_transaction.atomic
    def increase_credit_limit(customer, amount):
        """
        Increase the credit limit of a customer by a given amount.
        """
        try:
            if amount <= 0:
                raise ValueError("Increase amount must be greater than zero.")

            customer_account = CustomerAccount.objects.get(customer=customer)
            old_limit = customer_account.credit_limit
            customer_account.credit_limit += amount
            customer_account.save(update_fields=["credit_limit"])

            logger.info(
                f"Credit limit increased for Customer {customer.id} ({customer.first_name}): "
                f"{old_limit} -> {customer_account.credit_limit} (+{amount})"
            )

            return customer_account

        except CustomerAccount.DoesNotExist:
            logger.error(
                f"CustomerAccount not found for Customer {customer.id} ({customer.first_name})"
            )
            raise

        except Exception as e:
            logger.exception(
                f"Unexpected error increasing credit limit for Customer {customer.id} "
                f"({customer.first_name}): {str(e)}"
            )
            raise

    @staticmethod
    @db_transaction.atomic()
    def reduce_credit_limit(customer, amount):
        """
            Reduces customer credit limit by the specified amount.
        """
        try:
            if amount <= 0:
                raise ValueError("amount must be greater than zero.")

            customer_account = CustomerAccount.objects.get(customer=customer)
            old_limit = customer_account.credit_limit

            if amount > old_limit:
                raise ValueError("Reduction amount exceeds current credit limit.")

            customer_account.credit_limit -= amount
            customer_account.save(update_fields=["credit_limit"])

            logger.info(
                f"Credit limit reduced for Customer {customer.id} ({customer.first_name}): "
                f"{old_limit} -> {customer_account.credit_limit} (-{amount})"
            )

            return customer_account

        except CustomerAccount.DoesNotExist:
            logger.error(
                f"CustomerAccount not found for Customer {customer.id} ({customer.first_name})"
            )
            raise

        except Exception as e:
            logger.exception(
                f"Unexpected error reducing credit limit for Customer {customer.id} "
                f"({customer.first_name}): {str(e)}"
            )
            raise
        

    @staticmethod
    @db_transaction.atomic
    def validate_credit_limit(customer, amount):
        """
        Validates that the customer's credit limit can cover a given amount.
        Raises ValueError if the amount exceeds the limit.
        """
        try:
            if amount <= 0:
                raise ValueError("Amount must be greater than zero.")

            customer_account = CustomerAccount.objects.get(customer=customer)

            if amount > customer_account.credit_limit:
                raise ValueError(
                    f"Transaction amount {amount} exceeds credit limit "
                    f"of {customer_account.credit_limit} for Customer {customer.id} "
                    f"({customer.first_name})"
                )

            logger.info(
                f"Credit validation passed for Customer {customer.id} "
                f"({customer.first_name}): amount {amount}, limit {customer_account.credit_limit}"
            )

            return True

        except CustomerAccount.DoesNotExist:
            logger.error(
                f"CustomerAccount not found for Customer {customer.id} ({customer.first_name})"
            )
            raise

        except Exception as e:
            logger.exception(
                f"Unexpected error validating credit limit for Customer {customer.id} "
                f"({customer.first_name}): {str(e)}"
            )
            raise