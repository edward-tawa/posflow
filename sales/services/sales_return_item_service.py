from sales.models.sales_return_item_model import SalesReturnItem
from inventory.services.product_stock_service import ProductStockService
from django.db import transaction as db_transaction
from decimal import Decimal
from loguru import logger
from sales.models.sales_return_model import SalesReturn



class SalesReturnItemService:
    # Sales Return Item Management Service

    @staticmethod
    @db_transaction.atomic
    def create_sales_return_item(
        sales_return: SalesReturn,
        product,
        product_name: str,
        quantity: int,
        unit_price: Decimal,
        tax_rate: Decimal,
        status: str = "PENDING"
    ) -> SalesReturnItem:
        """
        Create a sales return item, adjust stock, and update parent return total.
        1. Create SalesReturnItem
        2. Increase stock for the returned item
        3. Update parent return total
        4. Return the created item
        """
        try:
            item = SalesReturnItem.objects.create(
                sales_return=sales_return,
                product=product,
                product_name=product_name,
                quantity=quantity,
                unit_price=unit_price,
                tax_rate=tax_rate,
                status=status
            )
            logger.info(
                f"Sales Return Item '{item.id}' created for return '{item.sales_return.return_number}'."
            )

            # Increase stock for the returned item
            ProductStockService.increase_stock_for_sales_return_item(item)

            # Update parent return total
            sales_return.update_total_amount()

            return item
        except Exception as e:
            logger.error(f"Error creating sales return item: {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def update_sales_return_item(
        item: SalesReturnItem,
        product=None,
        product_name: str = None,
        quantity: int = None,
        unit_price: Decimal = None,
        tax_rate: Decimal = None,
        status: str = None
    ) -> SalesReturnItem:
        
        """
        Update a sales return item, adjust stock if quantity changes, and update parent return total.
        1. Update SalesReturnItem fields
        2. Adjust stock if quantity changes
        3. Update parent return total if quantity or unit_price changes
        4. Return the updated item
        """
        
        old_quantity = item.quantity
        old_unit_price = item.unit_price
        try:
            fields_to_update = {}
            if product is not None:
                item.product = product
                fields_to_update["product"] = product
            if product_name is not None:
                item.product_name = product_name
                fields_to_update["product_name"] = product_name
            if quantity is not None:
                item.quantity = quantity
                fields_to_update["quantity"] = quantity
            if unit_price is not None:
                item.unit_price = unit_price
                fields_to_update["unit_price"] = unit_price
            if tax_rate is not None:
                item.tax_rate = tax_rate
                fields_to_update["tax_rate"] = tax_rate
            if status is not None:
                item.status = status
                fields_to_update["status"] = status

            if fields_to_update:
                item.save(update_fields=fields_to_update.keys())
                logger.info(f"Sales Return Item '{item.id}' updated with fields: {list(fields_to_update.keys())}")

            if quantity is not None and quantity != old_quantity:
                delta = quantity - old_quantity
                ProductStockService.adjust_stock_manually(
                    product=item.product,
                    company=item.sales_return.company,
                    branch=item.sales_return.branch,
                    quantity_change=delta,  # positive or negative
                    reason="Adjusted due to updated sales return item",
                )

            # Update parent return total if quantity or unit_price changed
            if quantity is not None or unit_price is not None:
                item.sales_return.update_total_amount()

            return item
        except Exception as e:
            logger.error(f"Error updating sales return item '{item.id}': {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def delete_sales_return_item(item: SalesReturnItem) -> None:
        """
        Delete a sales return item, adjust stock, and update parent return total.
        1. Decrease stock for the returned item
        2. Delete the SalesReturnItem
        3. Update parent return total
        """
        try:
            item_id = item.id
            sales_return = item.sales_return

            # Decrease stock for the returned item before deletion
            ProductStockService.decrease_stock_for_sales_return_item(item)
            item.delete()
            logger.info(f"Sales Return Item '{item_id}' deleted.")

            # Update parent return total
            sales_return.update_total_amount()
        except Exception as e:
            logger.error(f"Error deleting sales return item '{item.id}': {str(e)}")
            raise


    