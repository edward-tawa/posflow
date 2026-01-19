# from django.db import models
# from django.db.models import Q
from inventory.models.product_model import Product
from transactions.models.transaction_model import Transaction
from company.models.company_model import Company
from branch.models.branch_model import Branch
from accounts.models.account_model import Account
from customers.models.customer_model import Customer
from suppliers.models.supplier_model import Supplier
from accounts.services.account_service import AccountsService
# from rest_framework.response import Response
from loguru import logger
from decimal import Decimal
from django.db import transaction as db_transaction
# from config.pagination.pagination import StandardResultsSetPagination
from transactions.services.transaction_item_service import TransactionItemService



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
                    supplier: Supplier = None,
                    product: Product = None
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
            if transaction.transaction_type in [t[0] for t in Transaction.TRANSACTION_TYPE]:
                transaction_item = TransactionItemService.create_transaction_item(
                        transaction=transaction,
                        product=product,
                        product_name=product.name if product else "N/A",
                        quantity=1,
                        unit_price=product.unit_price if product else Decimal("0.00"),
                        )

                TransactionItemService.add_to_transaction(transaction_item, transaction)
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

            #Mark transaction as completed
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
    
    





