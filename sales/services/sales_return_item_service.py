from sales.models.sales_return_item_model import SalesReturnItem
from django.db import transaction as db_transaction
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from loguru import logger

from sales.models.sales_return_model import SalesReturn




class SalesReturnItemService:

    @staticmethod
    @db_transaction.atomic
    def create_sales_return_item(**kwargs) -> SalesReturnItem:
        try:
            item = SalesReturnItem.objects.create(**kwargs)
            logger.info(
                f"Sales Return Item '{item.id}' created for return '{item.sales_return.return_number}'."
            )
            return item
        except Exception as e:
            logger.error(f"Error creating sales return item: {str(e)}")
            raise
    

    @staticmethod
    @db_transaction.atomic
    def update_sales_return_item(item: SalesReturnItem, **kwargs) -> SalesReturnItem:
        try:
            for key, value in kwargs.items():
                setattr(item, key, value)
            item.save(update_fields=kwargs.keys())
            logger.info(f"Sales Return Item '{item.id}' updated.")
            return item
        except Exception as e:
            logger.error(f"Error updating sales return item '{item.id}': {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def delete_sales_return_item(item: SalesReturnItem) -> None:
        try:
            item_id = item.id
            item.delete()
            logger.info(f"Sales Return Item '{item_id}' deleted.")
        except Exception as e:
            logger.error(f"Error deleting sales return item '{item.id}': {str(e)}")
            raise
    
    @staticmethod
    @db_transaction.atomic
    def update_sales_return_item_status(item: SalesReturnItem, new_status: str) -> SalesReturnItem:
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
        previous_return = item.sales_return
        item.sales_return = sales_return
        item.save(update_fields=["sales_return"])
        
        if previous_return and previous_return != sales_return:
            previous_return.update_total_amount()
        sales_return.update_total_amount()

        logger.info(
            f"Sales Return Item '{item.id}' moved from return '{previous_return.return_number if previous_return else 'N/A'}' "
            f"to return '{sales_return.return_number}'."
        )
        return item
