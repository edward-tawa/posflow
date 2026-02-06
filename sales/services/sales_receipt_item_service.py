from inventory.models.product_model import Product
from sales.models.sales_order_model import SalesOrder
from sales.models.sales_receipt_item_model import SalesReceiptItem
from sales.models.sales_receipt_model import SalesReceipt
from django.db import transaction as db_transaction
from sales.models.sales_invoice_model import SalesInvoice
from inventory.services.product_stock_service import ProductStockService
from django.db.models import QuerySet
from loguru import logger



class SalesReceiptItemService:
    # Sales Receipt Item Management Service
    @staticmethod
    @db_transaction.atomic
    def create_sales_receipt_item(
        sales_receipt: SalesReceipt,
        product: Product,
        product_name: str,
        quantity: int,
        unit_price: float,
        tax_rate: float
    ) -> SalesReceiptItem:
        """
        Docstring for create_sales_receipt_item
        
        Create a sales receipt item.
        1. Create SalesReceiptItem
        2. Deduct stock for the sold item
        3. Update total amount on the receipt
        4. Return the created item
        """
        try:
            item = SalesReceiptItem.objects.create(
                sales_receipt=sales_receipt,
                product=product,
                product_name=product_name,
                quantity=quantity,
                unit_price=unit_price,
                tax_rate=tax_rate
            )
            
            logger.info(
                f"Sales Receipt Item '{item.id}' created for receipt '{sales_receipt.receipt_number}'."
            )
            
            # add/attach to sales receipt
            SalesReceiptItemService.add_item_to_receipt(
                item=item,
                receipt=sales_receipt
            )

            # Deduct stock for the sold item
            ProductStockService.decrease_stock_for_sale(item)

            # Update total amount on the receipt
            sales_receipt.update_total_amount()
            
            return item
        except Exception as e:
            logger.error(f"Error creating sales receipt item: {str(e)}")
            raise


    

    @staticmethod
    @db_transaction.atomic
    def create_sales_receipt_items(*,
        sales_receipt: SalesReceipt,
        items: QuerySet
    ) -> list[SalesReceiptItem]:
        """
        Create multiple sales receipt items at once.

        Args:
            sales_receipt: The SalesReceipt instance to attach items to.
            items_data: A list of dictionaries, each containing:
                - product: Product instance
                - product_name: str
                - quantity: int
                - unit_price: float
                - tax_rate: float

        Returns:
            List of created SalesReceiptItem instances.

        Process:
            1. Create all SalesReceiptItem objects
            2. Deduct stock for each sold item
            3. Update total amount on the receipt
            4. Return list of created items
        """
        created_items = []
        try:
            for item in items:
                item_obj = SalesReceiptItem.objects.create(
                    sales_receipt=sales_receipt,
                    product=item.product,
                    product_name=item.product_name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    tax_rate=item.tax_rate
                )
                logger.info(
                    f"Sales Receipt Item '{item_obj.id}' created for receipt '{sales_receipt.receipt_number}'."
                )

                # Attach item to receipt
                SalesReceiptItemService.add_item_to_receipt(
                    item=item_obj,
                    receipt=sales_receipt
                )

                # Deduct stock for this item
                ProductStockService.decrease_stock_for_sale(item_obj)

                created_items.append(item_obj)

            # Update total amount once after all items are added
            sales_receipt.update_total_amount()

            return created_items

        except Exception as e:
            logger.error(f"Error creating sales receipt items: {str(e)}")
            raise

    

    @staticmethod
    @db_transaction.atomic
    def update_sales_receipt_item(
        item: SalesReceiptItem,
        quantity: int = None,
        unit_price: float = None,
        tax_rate: float = None
    ) -> SalesReceiptItem:
        """
        Docstring for update_sales_receipt_item
        
        Update a sales receipt item.
        1. Update SalesReceiptItem fields.
        2. Return the updated item.
        """
        old_quantity = item.quantity
        try:
            if quantity is not None:
                item.quantity = quantity
            if unit_price is not None:
                item.unit_price = unit_price
            if tax_rate is not None:
                item.tax_rate = tax_rate


            if quantity is not None and quantity != old_quantity:
                # Adjust stock if quantity has changed
                difference = quantity - old_quantity
                ProductStockService.adjust_stock_manually(
                    product=item.product,
                    company=item.sales_receipt.company,
                    branch=item.sales_receipt.branch,
                    quantity_change=difference,
                    reason=f"Adjustment due to update of Sales Receipt Item '{item.id}'"
                    )
            item.save(update_fields=[k for k in ['quantity', 'unit_price', 'tax_rate'] if k])
            logger.info(f"Sales Receipt Item '{item.id}' updated.")
            return item
        except Exception as e:
            logger.error(f"Error updating sales receipt item '{item.id}': {str(e)}")
            raise


    @staticmethod
    @db_transaction.atomic
    def delete_sales_receipt_item(item: SalesReceiptItem) -> None:
        """
        Docstring for delete_sales_receipt_item
        
        Delete a sales receipt item.
        1. Delete the SalesReceiptItem.
        2. Return None.
        """
        try:
            item_id = item.id
            # decrease stock for the sold item
            ProductStockService.increase_stock_for_voided_sale_item(item)
            item.delete()
            logger.info(f"Sales Receipt Item '{item_id}' deleted.")
        except Exception as e:
            logger.error(f"Error deleting sales receipt item '{item.id}': {str(e)}")
            raise


    
    @staticmethod
    @db_transaction.atomic
    def add_item_to_receipt(item: SalesReceiptItem, receipt: SalesReceipt) -> SalesReceiptItem:
        """
        Docstring for add_item_to_receipt
        
        Attach a sales receipt item to a sales receipt.
        1. Update the item's sales_receipt field
        2. Return the updated item
        """
        try:
            item.sales_receipt = receipt
            item.save(update_fields=["sales_receipt"])
            logger.info(
                f"Sales Receipt Item '{item.id}' added to receipt '{receipt.receipt_number}'."
            )
            return item
        except Exception as e:
            logger.error(
                f"Error adding sales receipt item '{item.id}' to receipt '{receipt.receipt_number}': {str(e)}"
            )
            raise

    @staticmethod
    @db_transaction.atomic
    def remove_item_from_receipt(item: SalesReceiptItem, receipt: SalesReceipt) -> SalesReceiptItem:
        """
        Docstring for remove_item_from_receipt
        Detach a sales receipt item from a sales receipt.
        1. Clear the item's sales_receipt field
        2. Return the updated item
        """
        try:
            if item.sales_receipt != receipt:
                logger.warning(
                    f"Sales Receipt Item '{item.id}' is not attached to receipt '{receipt.receipt_number}'."
                )
                return item

            item.sales_receipt = None
            item.save(update_fields=["sales_receipt"])
            logger.info(
                f"Sales Receipt Item '{item.id}' removed from receipt '{receipt.receipt_number}'."
            )
            return item
        except Exception as e:
            logger.error(
                f"Error removing sales receipt item '{item.id}' from receipt '{receipt.receipt_number}': {str(e)}"
            )
            raise


    @staticmethod
    @db_transaction.atomic
    def bulk_create_receipt_items(items_data: list[dict], receipt: SalesReceipt) -> list[SalesReceiptItem]:
        """
        Docstring for bulk_create_receipt_items
        
        Bulk create sales receipt items for a given receipt.
        1. Create multiple SalesReceiptItem instances
        2. Return the list of created items
        """
        items = [SalesReceiptItem(sales_receipt=receipt, **data) for data in items_data]
        SalesReceiptItem.objects.bulk_create(items)
        for item in items:
            # Deduct stock for each sold item
            ProductStockService.decrease_stock_for_sale(item)
        # Update total amount on the receipt
        receipt.update_total_amount()
        logger.info(f"Bulk created {len(items)} items for receipt '{receipt.receipt_number}'.")
        return items



    @staticmethod
    @db_transaction.atomic
    def add_order_items_to_receipt(order: SalesOrder, receipt: SalesReceipt) -> list[SalesReceiptItem]:
        """
        Add all items from a SalesOrder to a SalesReceipt.
        1. Creates new SalesReceiptItems for each order item.
        2. Deducts stock automatically via create_sales_receipt_item().
        3. Returns the list of created receipt items.
        """
        items_created = []
        for order_item in order.items.all():
            item = SalesReceiptItemService.create_sales_receipt_item(
                sales_receipt=receipt,
                product=order_item.product,
                product_name=order_item.product_name,
                quantity=order_item.quantity,
                unit_price=order_item.unit_price,
                tax_rate=order_item.tax_rate
            )
            items_created.append(item)

        logger.info(
            f"Added {len(items_created)} items from Order '{order.order_number}' "
            f"to Receipt '{receipt.receipt_number}'."
        )
        return items_created




    @staticmethod
    @db_transaction.atomic
    def add_invoice_items_to_receipt(invoice: SalesInvoice, receipt: SalesReceipt) -> list[SalesReceiptItem]:
        """
        Add all items from a SalesInvoice to a SalesReceipt.
        1. Creates new SalesReceiptItems for each invoice item.
        2. Deducts stock automatically via create_sales_receipt_item() if needed.
        3. Returns the list of created receipt items.
        """
        items_created = []
        for invoice_item in invoice.items.all():
            item = SalesReceiptItemService.create_sales_receipt_item(
                sales_receipt=receipt,
                product=invoice_item.product,
                product_name=invoice_item.product_name,
                quantity=invoice_item.quantity,
                unit_price=invoice_item.unit_price,
                tax_rate=invoice_item.tax_rate
            )
            items_created.append(item)

        logger.info(
            f"Added {len(items_created)} items from Invoice '{invoice.invoice_number}' "
            f"to Receipt '{receipt.receipt_number}'."
        )
        return items_created
