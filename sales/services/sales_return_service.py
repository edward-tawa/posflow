from inventory.services.product_stock_service import ProductStockService
from sales.models.sales_return_model import SalesReturn
from accounts.models.sales_returns_account_model import SalesReturnsAccount
from transactions.services.transaction_service import TransactionService
from django.db import transaction as db_transaction
from decimal import Decimal
from django.utils import timezone
from loguru import logger


class SalesReturnService:
    """
    Service class for managing sales returns.
    Provides methods for creating, updating, reversing, and managing sales returns.
    """

    ALLOWED_STATUSES = {"DRAFT", "APPROVED", "CANCELLED"}
    ALLOWED_UPDATE_FIELDS = {"return_date", "notes", "total_amount", "processed_by", "sale", "sale_order", "customer", "branch", "company"}

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def create_sales_return(
        company,
        branch,
        customer,
        sale_order,
        sale=None,
        return_date=None,
        total_amount=Decimal("0.00"),
        processed_by=None,
        notes=None,
        status=None  # Optional status
    ) -> SalesReturn:
        try:
            if return_date is None:
                return_date = timezone.now().date()

            sales_return = SalesReturn.objects.create(
                company=company,
                branch=branch,
                customer=customer,
                sale_order=sale_order,
                sale=sale,
                return_date=return_date,
                total_amount=total_amount,
                processed_by=processed_by,
                notes=notes
            )

            # Increase stock for returned items
            ProductStockService.increase_stock_for_sales_return(sales_return=sales_return)

            # Determine accounts
            sales_return_account = SalesReturnsAccount.objects.get(company=company, branch=branch)

            # Create transaction
            transaction = TransactionService.create_transaction(
                company=company,
                branch=branch,
                debit_account=sales_return_account.account,
                credit_account=customer.customer_account.account,
                transaction_type="SALES_RETURN",
                transaction_category="SALES_RETURN",
                total_amount=sales_return.total_amount,
                customer=customer
            )

            TransactionService.apply_transaction_to_accounts(transaction)

            # Update status if provided
            if status:
                SalesReturnService.update_sales_return_status(sales_return, new_status=status)

            logger.info(f"Sales Return '{sales_return.return_number}' created for company '{company.name}'.")
            return sales_return

        except Exception as e:
            logger.error(f"Error creating sales return: {str(e)}")
            raise

    # -------------------------
    # UPDATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_sales_return(sales_return: SalesReturn, status=None, **kwargs) -> SalesReturn:
        try:
            update_data = {k: v for k, v in kwargs.items() if k in SalesReturnService.ALLOWED_UPDATE_FIELDS}
            if update_data:
                for key, value in update_data.items():
                    setattr(sales_return, key, value)
                sales_return.save(update_fields=update_data.keys())
                logger.info(f"Sales Return '{sales_return.return_number}' updated with fields: {list(update_data.keys())}")

            # Only update status via centralized method
            if status:
                SalesReturnService.update_sales_return_status(sales_return, new_status=status)

            return sales_return
        except Exception as e:
            logger.error(f"Error updating sales return '{sales_return.return_number}': {str(e)}")
            raise

    # -------------------------
    # STATUS MANAGEMENT
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def update_sales_return_status(sales_return: SalesReturn, new_status: str) -> SalesReturn:
        if new_status not in SalesReturnService.ALLOWED_STATUSES:
            logger.error(f"Attempted to set invalid status '{new_status}' for sales return '{sales_return.return_number}'")
            raise ValueError(f"Invalid status: {new_status}")

        sales_return.status = new_status
        sales_return.save(update_fields=["status"])
        logger.info(f"Sales Return '{sales_return.return_number}' status updated to '{new_status}'.")
        return sales_return

    # -------------------------
    # REVERSE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def reverse_sales_return(sales_return: SalesReturn, performed_by) -> SalesReturn:
        if getattr(sales_return, "status", None) == "CANCELLED":
            raise ValueError(f"Sales Return '{sales_return.return_number}' is already cancelled.")

        # Adjust stock manually for all items
        for item in sales_return.items.select_related("product"):
            ProductStockService.adjust_stock_manually(
                product=item.product,
                company=sales_return.company,
                branch=sales_return.branch,
                quantity_change=-item.quantity,
                reason=f"Reversal of Sales Return {sales_return.return_number}",
                performed_by=performed_by
            )

        # Reverse associated transaction
        original_transaction = TransactionService.get_transactions_by_category(
            transaction_category="SALES_RETURN",
            company=sales_return.company,
            branch=sales_return.branch
        ).filter(customer=sales_return.customer).last()

        if original_transaction:
            TransactionService.reverse_transaction(original_transaction)

        # Mark sales return as cancelled
        SalesReturnService.update_sales_return_status(sales_return, new_status="CANCELLED")

        logger.info(f"Sales Return '{sales_return.return_number}' reversed successfully.")
        return sales_return
