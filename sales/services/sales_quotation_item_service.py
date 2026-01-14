from sales.models.sales_quotation_item_model import SalesQuotationItem
from sales.models.sales_quotation_model import SalesQuotation
from sales.models.sales_invoice_model import SalesInvoice
from django.db import transaction as db_transaction
from loguru import logger


class SalesQuotationItemService:
    # Sales Quotation Item Management Service

    @staticmethod
    @db_transaction.atomic
    def create_sales_quotation_item(
        sales_quotation: SalesQuotation,
        product_name: str,
        quantity: int,
        unit_price: float,
        tax_rate: float,
        sales_invoice: SalesInvoice = None
    ) -> SalesQuotationItem:
        """
        Docstring for create_sales_quotation_item
        Create a sales quotation item.
        1. Create SalesQuotationItem
        2. Update total amount on the quotation
        3. Return the created item
        """
        try:
            item = SalesQuotationItem.objects.create(
                sales_quotation=sales_quotation,
                product_name=product_name,
                quantity=quantity,
                unit_price=unit_price,
                tax_rate=tax_rate,
                sales_invoice=sales_invoice
            )
            logger.info(
                f"Sales Quotation Item '{item.id}' created for quotation '{sales_quotation.quotation_number}'."
            )
            sales_quotation.update_total_amount()
            return item
        except Exception as e:
            logger.error(f"Error creating sales quotation item: {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def update_sales_quotation_item(
        item: SalesQuotationItem,
        product_name: str = None,
        quantity: int = None,
        unit_price: float = None,
        tax_rate: float = None
    ) -> SalesQuotationItem:
        """
        Docstring for update_sales_quotation_item
        
        Update a SalesQuotationItem with provided fields.
        Only non-None arguments will be applied.
        1. Update fields on SalesQuotationItem
        2. Recalculate total amount on parent quotation
        3. Return the updated item
        """
        try:
            update_fields = []

            if product_name is not None:
                item.product_name = product_name
                update_fields.append('product_name')

            if quantity is not None:
                item.quantity = quantity
                update_fields.append('quantity')

            if unit_price is not None:
                item.unit_price = unit_price
                update_fields.append('unit_price')

            if tax_rate is not None:
                item.tax_rate = tax_rate
                update_fields.append('tax_rate')

            if update_fields:
                item.save(update_fields=update_fields)
                logger.info(f"Sales Quotation Item '{item.id}' updated: {update_fields}")

                # Recalculate total ONCE, after persistence
                if item.sales_quotation:
                    item.sales_quotation.update_total_amount()

            return item

        except Exception as e:
            logger.error(f"Error updating sales quotation item '{item.id}': {str(e)}")
            raise



    @staticmethod
    @db_transaction.atomic
    def delete_sales_quotation_item(item: SalesQuotationItem) -> None:
        """
        Docstring for delete_sales_quotation_item
        
        Delete a sales quotation item and update parent quotation total.
        1. Delete SalesQuotationItem
        2. Update parent quotation total
        3. Log the deletion
        4. Handle exceptions
        """
        util_quotation_item = item
        try:
            quotation_number = util_quotation_item.sales_quotation.quotation_number if util_quotation_item.sales_quotation else "N/A"
            util_quotation_item.delete()
            logger.info(f"Sales Quotation Item '{util_quotation_item.id}' deleted from quotation '{quotation_number}'.")
            if util_quotation_item.sales_quotation:
                util_quotation_item.sales_quotation.update_total_amount()
        except Exception as e:
            logger.error(f"Error deleting sales quotation item '{util_quotation_item.id}': {str(e)}")
            raise
    

    @staticmethod
    @db_transaction.atomic
    def add_quotation_items_to_quotation(sales_quotation: SalesQuotation, items: list[SalesQuotationItem]) -> None:
        """
        Docstring for add_quotation_items_to_quotation
        
        Add all existing quotation items to the sales quotation.
        """
        try:
            for item in items:
                item.sales_quotation = sales_quotation
                item.save(update_fields=["sales_quotation"])
            sales_quotation.update_total_amount()
            logger.info(f"Added {len(items)} items to Sales Quotation '{sales_quotation.quotation_number}'.")
        except Exception as e:
            logger.error(f"Error adding items to sales quotation '{sales_quotation.quotation_number}': {str(e)}")
            raise