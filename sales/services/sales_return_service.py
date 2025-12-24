from sales.models.sales_return_model import SalesReturn
from django.db import transaction as db_transaction
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from loguru import logger



class SalesReturnService:

    @staticmethod
    @db_transaction.atomic
    def create_sales_return(**kwargs) -> SalesReturn:
        try:
            sales_return = SalesReturn.objects.create(**kwargs)
            logger.info(
                f"Sales Return '{sales_return.return_number}' created for company '{sales_return.company.name}'."
            )
            return sales_return
        except Exception as e:
            logger.error(f"Error creating sales return: {str(e)}")
            raise
    

    @staticmethod
    @db_transaction.atomic
    def update_sales_return(sales_return: SalesReturn, **kwargs) -> SalesReturn:
        try:
            for key, value in kwargs.items():
                setattr(sales_return, key, value)
            sales_return.save(update_fields=kwargs.keys())
            logger.info(f"Sales Return '{sales_return.return_number}' updated.")
            return sales_return
        except Exception as e:
            logger.error(f"Error updating sales return '{sales_return.return_number}': {str(e)}")
            raise
    

    @staticmethod
    @db_transaction.atomic
    def delete_sales_return(sales_return: SalesReturn) -> None:
        try:
            return_number = sales_return.return_number
            sales_return.delete()
            logger.info(f"Sales Return '{return_number}' deleted.")
        except Exception as e:
            logger.error(f"Error deleting sales return '{sales_return.return_number}': {str(e)}")
            raise
    

    @staticmethod
    @db_transaction.atomic
    def update_sales_return_status(sales_return: SalesReturn, new_status: str) -> SalesReturn:
        try:
            sales_return.status = new_status
            sales_return.save(update_fields=["status"])
            logger.info(f"Sales Return '{sales_return.return_number}' status updated to '{new_status}'.")
            return sales_return
        except Exception as e:
            logger.error(f"Error updating status for sales return '{sales_return.return_number}': {str(e)}")
            raise
    

    @staticmethod
    @db_transaction.atomic
    def restore_stock_for_return(sales_return: SalesReturn) -> None:
        """
        Restores stock for all products in a given sales return.
        Useful if the return was voided or needs to be reversed.
        """
        try:
            for item in sales_return.items.all():
                product = item.product
                product.stock += item.quantity
                product.save(update_fields=['stock'])
                logger.info(
                    f"Restored {item.quantity} to stock of '{product.name}'."
                    f"New stock: {product.stock}"
                )

            logger.info(f"Stock restored for all items in sales return '{sales_return.return_number}'")
        except Exception as e:
            logger.error(f"Error restoring stock for sales return '{sales_return.return_number}': {str(e)}")
            raise
