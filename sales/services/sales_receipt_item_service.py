from sales.models.sales_receipt_item_model import SalesReceiptItem
from sales.models.sales_receipt_model import SalesReceipt
from django.db import transaction as db_transaction
from loguru import logger



class SalesReceiptItemService:

    @staticmethod
    @db_transaction.atomic
    def create_sales_receipt_item(**kwargs) -> SalesReceiptItem:
        try:
            item = SalesReceiptItem.objects.create(**kwargs)
            logger.info(
                f"Sales Receipt Item '{item.id}' created for receipt '{item.sales_receipt.receipt_number}'."
            )
            return item
        except Exception as e:
            logger.error(f"Error creating sales receipt item: {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def update_sales_receipt_item(item: SalesReceiptItem, **kwargs) -> SalesReceiptItem:
        try:
            for key, value in kwargs.items():
                setattr(item, key, value)
            item.save(update_fields=kwargs.keys())
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





    
