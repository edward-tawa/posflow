from sales.models.sales_order_item_model import SalesOrderItem
from sales.models.sales_order_model import SalesOrder
from django.db import transaction as db_transaction
from inventory.models import Product
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from loguru import logger


class SalesOrderItemService:
    """
    Service class for managing sales order items.
    Provides methods for creating, updating, and deleting sales order items.
    Includes detailed logging for key operations.
    """


class SalesOrderItemService:
    """
    Service class for managing sales order items.
    Provides methods for creating, updating, and deleting sales order items.
    """

    @staticmethod
    @db_transaction.atomic
    def create_sales_order_item(
        sales_order: SalesOrder,
        product: Product,
        product_name: str,
        quantity: int,
        unit_price: float,
        tax_rate: float
    ) -> SalesOrderItem:
        """
        Docstring for create_sales_order_item
        
        Create a sales order item.
        1. Create SalesOrderItem
        2. Log the creation
        3. Return the created item
        """
        try:
            item = SalesOrderItem.objects.create(
                sales_order=sales_order,
                product=product,
                product_name=product_name,
                quantity=quantity,
                unit_price=unit_price,
                tax_rate=tax_rate
            )

            logger.info(
                f"Sales Order Item '{item.id}' created for order '{sales_order.order_number}'."
            )

            # Add/attach to sales order
            SalesOrderItemService.add_sales_order_item_to_sales_order(
                item=item,
                sales_order=sales_order
            )

            # Update total amount on the order
            sales_order.update_total_amount()
            return item
        
        except Exception as e:
            logger.error(f"Error creating sales order item: {str(e)}")
            raise
        

    @staticmethod
    @db_transaction.atomic
    def update_sales_order_item(
        item: SalesOrderItem,
        quantity: int = None,
        unit_price: float = None,
        tax_rate: float = None
    ) -> SalesOrderItem:
        """
        Docstring for update_sales_order_item
        Update a SalesOrderItem with provided fields.
        Only non-None arguments will be applied.
        1. Update fields on SalesOrderItem
        2. Log the update
        3. Return the updated item
        """
        try:
            if quantity is not None:
                item.quantity = quantity
            if unit_price is not None:
                item.unit_price = unit_price
            if tax_rate is not None:
                item.tax_rate = tax_rate

            item.save(update_fields=[k for k in ['quantity', 'unit_price', 'tax_rate'] if getattr(item, k) is not None])
            logger.info(f"Sales Order Item '{item.id}' updated.")

            # Update total amount on the order
            item.sales_order.update_total_amount()

            return item
        except Exception as e:
            logger.error(f"Error updating sales order item '{item.id}': {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def delete_sales_order_item(item: SalesOrderItem) -> None:
        """
        Docstring for delete_sales_order_item
        Delete a SalesOrderItem.
        1. Delete the item
        2. Log the deletion
        3. Return None
        """
        try:
            item_id = item.id
            item.delete()
            logger.info(f"Sales Order Item '{item_id}' deleted.")

            # Update total amount on the order
            item.sales_order.update_total_amount()
        except Exception as e:
            logger.error(f"Error deleting sales order item '{item.id}': {str(e)}")
            raise

    

    @staticmethod
    @db_transaction.atomic
    def update_sales_order_item_status(item: SalesOrderItem, new_status: str) ->SalesOrderItem:
        """
        Docstring for update_sales_order_item_status
        
        Update the status of a SalesOrderItem.
        1. Update status field
        2. Log the update
        3. Return the updated item
        """
        try:
            item.status = new_status
            item.save(update_fields=["status"])
            logger.info(f"Sales Order Item '{item.id}' status updated to '{new_status}'.")
            return item
        except Exception as e:
            logger.error(f"Error updating status for sales order item '{item.id}': {str(e)}")
            raise
    


    @staticmethod
    @db_transaction.atomic
    def add_sales_order_item_to_sales_order(item: SalesOrderItem, sales_order: SalesOrder) -> SalesOrderItem:
        """
        Docstring for add_sales_order_item_to_sales_order
        Attach a SalesOrderItem to a SalesOrder.
        1. Update SalesOrderItem's sales_order field
        2. Log the attachment
        3. Return the updated item
        """
        try:
            previous_order = item.sales_order

            item.sales_order = sales_order
            item.save(update_fields=["sales_order"])

            if previous_order and previous_order != sales_order:
                previous_order.update_total_amount()

            logger.info(
                f"Sales Order Item '{item.id}' attached to Sales Order '{sales_order.order_number}'."
            )
            return item
        except Exception as e:
            logger.error(
                f"Error attaching Sales Order Item '{item.id}' to Sales Order '{sales_order.order_number}': {str(e)}"
            )
            raise
    

    

    
    # @staticmethod
    # @db_transaction.atomic
    # def calculate_total_price(item: SalesOrderItem) -> Decimal:
    #     """
    #     Calculates the total price for a sales order item based on quantity and unit price.
    #     Rounds the result to two decimal places.
        
    #     Args:
    #         item (SalesOrderItem): The sales order item to calculate total price for.
    #     Returns:
    #         Decimal: The total price rounded to two decimal places.
    #     """
    #     try:
    #         total_price = item.quantity * item.unit_price
    #         rounded_price = total_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    #         logger.info(f"Total price for Sales Order Item '{item.id}' calculated: {rounded_price}")
    #         return rounded_price
    #     except Exception as e:
    #         logger.error(f"Error calculating total price for Sales Order Item '{item.id}': {str(e)}")
    #         raise