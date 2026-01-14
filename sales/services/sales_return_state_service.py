from django.db import transaction as db_transaction
from loguru import logger
from sales.models.sales_return_item_model import SalesReturnItem
from sales.models.sales_return_model import SalesReturn
from sales.services.sales_return_service import SalesReturnService




class SalesReturnStateService:
    ALLOWED_STATUSES = {"DRAFT", "APPROVED", "CANCELLED"}

    @staticmethod
    @db_transaction.atomic
    def update_sales_return_status(sales_return: SalesReturn, new_status: str) -> SalesReturn:
        """
        Docstring for update_sales_return_status
        Update the status of a sales return.
        1. Validate new status
        2. Update the sales return's status
        3. Return the updated sales return
        
        """
        if new_status not in SalesReturnStateService.ALLOWED_STATUSES:
            logger.error(
                f"Attempted to set invalid status '{new_status}' for sales return '{sales_return.return_number}'"
            )
            raise ValueError(f"Invalid status: {new_status}")

        sales_return.status = new_status
        sales_return.save(update_fields=["status"])
        logger.info(
            f"Sales Return '{sales_return.return_number}' status updated to '{new_status}'."
        )
        return sales_return


    @staticmethod
    @db_transaction.atomic
    def update_sales_return_item_status(item: SalesReturnItem, new_status: str) -> SalesReturnItem:
        """
        Update the status of a sales return item.
        1. Validate new status
        2. Update the item's status
        3. Return the updated item
        """
        try:
            item.status = new_status
            item.save(update_fields=["status"])
            logger.info(f"Sales Return Item '{item.id}' status updated to '{new_status}'.")
            return item
        except Exception as e:
            logger.error(f"Error updating status for sales return item '{item.id}': {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def attach_to_sales_return(item: SalesReturnItem, sales_return: SalesReturn) -> SalesReturnItem:
        """
        Docstring for attach_to_sales_return

        Attach a sales return item to a different sales return and update totals accordingly.
        1. Update the item's sales_return field
        2. Update total amounts for both previous and new sales returns
        3. Return the updated item
        """
        previous_return = item.sales_return
        item.sales_return = sales_return
        item.save(update_fields=["sales_return"])

        if previous_return and previous_return != sales_return:
            previous_return.update_total_amount()
        sales_return.update_total_amount()

        logger.info(
            f"Sales Return Item '{item.id}' moved from return "
            f"'{previous_return.return_number if previous_return else 'N/A'}' "
            f"to return '{sales_return.return_number}'."
        )
        return item