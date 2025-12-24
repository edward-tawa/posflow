from inventory.models.product_model import Product
from sales.models.sales_order_model import SalesOrder
from sales.models.sales_receipt_item_model import SalesReceiptItem
from sales.models.sales_receipt_model import SalesReceipt
from django.db import transaction as db_transaction
from sales.models.sales_invoice_model import SalesInvoice
from loguru import logger



class SalesReceiptItemService:

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
            return item
        except Exception as e:
            logger.error(f"Error creating sales receipt item: {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def update_sales_receipt_item(
        item: SalesReceiptItem,
        quantity: int = None,
        unit_price: float = None,
        tax_rate: float = None
    ) -> SalesReceiptItem:
        try:
            if quantity is not None:
                item.quantity = quantity
            if unit_price is not None:
                item.unit_price = unit_price
            if tax_rate is not None:
                item.tax_rate = tax_rate

            item.save(update_fields=[k for k in ['quantity', 'unit_price', 'tax_rate'] if k])
            logger.info(f"Sales Receipt Item '{item.id}' updated.")
            return item
        except Exception as e:
            logger.error(f"Error updating sales receipt item '{item.id}': {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def delete_sales_receipt_item(item: SalesReceiptItem) -> None:
        try:
            item_id = item.id
            item.delete()
            logger.info(f"Sales Receipt Item '{item_id}' deleted.")
        except Exception as e:
            logger.error(f"Error deleting sales receipt item '{item.id}': {str(e)}")
            raise


    
    @staticmethod
    @db_transaction.atomic
    def attach_to_receipt(item: SalesReceiptItem, receipt: SalesReceipt) -> SalesReceiptItem:
        try:
            item.sales_receipt = receipt
            item.save(update_fields=["sales_receipt"])
            logger.info(
                f"Sales Receipt Item '{item.id}' attached to receipt '{receipt.receipt_number}'."
            )
            return item
        except Exception as e:
            logger.error(
                f"Error attaching sales receipt item '{item.id}' to receipt '{receipt.receipt_number}': {str(e)}"
            )
            raise

    
    @staticmethod
    @db_transaction.atomic
    def calculate_totals(item: SalesReceiptItem) -> dict:
        subtotal = item.subtotal
        tax = item.tax_amount
        total = item.total_price
        logger.info(f"Calculated totals for item '{item.id}': subtotal={subtotal}, tax={tax}, total={total}")
        return {"subtotal": subtotal, "tax": tax, "total": total}
    


    @staticmethod
    @db_transaction.atomic
    def bulk_create_receipt_items(items_data: list[dict], receipt: SalesReceipt) -> list[SalesReceiptItem]:
        items = [SalesReceiptItem(sales_receipt=receipt, **data) for data in items_data]
        SalesReceiptItem.objects.bulk_create(items)
        logger.info(f"Bulk created {len(items)} items for receipt '{receipt.receipt_number}'.")
        return items



    @staticmethod
    @db_transaction.atomic
    def add_order_items_to_receipt(order: SalesOrder, receipt: SalesReceipt):
        for order_item in order.items.all():
            SalesReceiptItemService.create_sales_receipt_item(
                sales_receipt=receipt,
                product=order_item.product,
                product_name=order_item.product_name,
                quantity=order_item.quantity,
                unit_price=order_item.unit_price,
                tax_rate=order_item.tax_rate
            )
        logger.info(f"Added {order.items.count()} items from Order '{order.order_number}' to Receipt '{receipt.receipt_number}'.")


    
    @staticmethod
    @db_transaction.atomic
    def add_invoice_items_to_receipt(invoice: SalesInvoice, receipt: SalesReceipt):
        """
        Copies all items from a SalesInvoice to a SalesReceipt.
        
        This ensures the receipt reflects exactly what was invoiced and paid for.
        """
        try:
            items_created = []
            for invoice_item in invoice.items.all():
                item = SalesReceiptItem.objects.create(
                    sales_receipt=receipt,
                    product=invoice_item.product,
                    product_name=invoice_item.product_name,
                    quantity=invoice_item.quantity,
                    unit_price=invoice_item.unit_price,
                    tax_rate=invoice_item.tax_rate
                )
                items_created.append(item)

            # Optionally update receipt total
            total = sum(item.subtotal + item.tax_amount for item in items_created)
            receipt.total_amount = total
            receipt.save(update_fields=['total_amount'])

            logger.info(
                f"Added {len(items_created)} items from Invoice '{invoice.invoice_number}' to Receipt '{receipt.receipt_number}'."
            )
            return items_created
        except Exception as e:
            logger.error(
                f"Error adding items from Invoice '{invoice.invoice_number}' to Receipt '{receipt.receipt_number}': {str(e)}"
            )
            raise