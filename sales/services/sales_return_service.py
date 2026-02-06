from inventory.services.product_stock.product_stock_service import ProductStockService
from sales.models.sales_return_item_model import SalesReturnItem
from sales.models.sales_return_model import SalesReturn
from accounts.models.sales_returns_account_model import SalesReturnsAccount
from sales.services.sales_return_item_service import SalesReturnItemService
from sales.services.sales_return_state_service import SalesReturnStateService
from transactions.services.transaction_service import TransactionService
from django.db import transaction as db_transaction
from decimal import Decimal
from django.utils import timezone
from loguru import logger


class SalesReturnService:
    """
    Service class for managing sales returns.
    Handles creation, updating, and reversing of sales returns.
    """

    ALLOWED_UPDATE_FIELDS = ["return_date", "notes", "total_amount"]

    # -------------------------
    # CREATE
    # -------------------------
    @staticmethod
    @db_transaction.atomic
    def create_sales_return(
        company,
        branch,
        customer,
        sales_order,
        sale=None,
        return_date=None,
        processed_by=None,
        notes=None,
        status=None
    ) -> SalesReturn:
        """
        Create a sales return with a single item.
        Automatically creates the sales return item, adjusts stock, and creates accounting transaction.
        """
        try:
            if return_date is None:
                return_date = timezone.now().date()

            # Create SalesReturn
            sales_return = SalesReturn.objects.create(
                company=company,
                branch=branch,
                customer=customer,
                sales_order=sales_order,
                sale=sale,
                return_date=return_date,
                total_amount=Decimal("0.00"),  # will calculate after creating item
                processed_by=processed_by,
                notes=notes
            )


            # Accounting transaction
            sales_return_account = SalesReturnsAccount.objects.get(company=company, branch=branch)
            transaction = TransactionService.create_transaction(
                company=company,
                branch=branch,
                debit_account=sales_return_account.account,
                credit_account=customer.customer_account.account,
                transaction_type="SALES_RETURN",
                transaction_category="SALES_RETURN",
                total_amount=sales_return.total_amount,
                customer=customer,
            )
            TransactionService.apply_transaction_to_accounts(transaction)

            # Update status if provided
            if status:
                SalesReturnStateService.update_sales_return_status(sales_return, new_status=status)

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
                SalesReturnStateService.update_sales_return_status(sales_return, new_status=status)

            return sales_return
        except Exception as e:
            logger.error(f"Error updating sales return '{sales_return.return_number}': {str(e)}")
            raise
    



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
        SalesReturnStateService.update_sales_return_status(sales_return, new_status="CANCELLED")

        logger.info(f"Sales Return '{sales_return.return_number}' reversed successfully.")
        return sales_return



    