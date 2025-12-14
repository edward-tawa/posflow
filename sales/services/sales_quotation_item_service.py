from sales.models.sales_quotation_item_model import SalesQuotationItem
from sales.models.sales_quotation_model import SalesQuotation
from sales.models.sales_invoice_model import SalesInvoice
from django.db import transaction as db_transaction
from loguru import logger


class SalesQuotationItemService:

    @staticmethod
    @db_transaction.atomic
    def create_sales_quotation_item(**kwargs) -> SalesQuotationItem:
        try:
            item = SalesQuotationItem.objects.create(**kwargs)
            logger.info(
                f"Sales Quotation Item '{item.id}' created for quotation '{item.sales_quotation.quotation_number}'."
            )
            return item
        except Exception as e:
            logger.error(f"Error creating sales quotation item: {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def update_sales_quotation_item(item: SalesQuotationItem, **kwargs) -> SalesQuotationItem:
        try:
            for key, value in kwargs.items():
                setattr(item, key, value)
            item.save(update_fields=kwargs.keys())
            logger.info(f"Sales Quotation Item '{item.id}' updated.")
            if item.sales_quotation:
                item.sales_quotation.update_total_amount()
            return item
        except Exception as e:
            logger.error(f"Error updating sales quotation item '{item.id}': {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def delete_sales_quotation_item(item: SalesQuotationItem) -> None:
        try:
            quotation = item.sales_quotation
            item_id = item.id
            item.delete()
            logger.info(f"Sales Quotation Item '{item_id}' deleted.")
            if quotation:
                quotation.update_total_amount()
        except Exception as e:
            logger.error(f"Error deleting sales quotation item '{item.id}': {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def attach_to_sales_quotation(item: SalesQuotationItem, sales_quotation: SalesQuotation) -> SalesQuotationItem:
        try:
            previous_quotation = item.sales_quotation
            item.sales_quotation = sales_quotation
            item.save(update_fields=["sales_quotation"])
            
            # Update totals
            if previous_quotation and previous_quotation != sales_quotation:
                previous_quotation.update_total_amount()
            sales_quotation.update_total_amount()

            logger.info(
                f"Sales Quotation Item '{item.id}' moved from quotation "
                f"'{previous_quotation.quotation_number if previous_quotation else 'N/A'}' "
                f"to quotation '{sales_quotation.quotation_number}'."
            )
            return item
        except Exception as e:
            logger.error(f"Error attaching sales quotation item '{item.id}': {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def attach_to_sales_invoice(item: SalesQuotationItem, sales_invoice: SalesInvoice) -> SalesQuotationItem:
        try:
            item.sales_invoice = sales_invoice
            item.save(update_fields=["sales_invoice"])
            logger.info(
                f"Sales Quotation Item '{item.id}' attached to invoice '{sales_invoice.invoice_number}'."
            )
            return item
        except Exception as e:
            logger.error(f"Error attaching sales quotation item '{item.id}' to invoice: {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def detach_from_sales_invoice(item: SalesQuotationItem) -> SalesQuotationItem:
        try:
            previous_invoice = item.sales_invoice
            item.sales_invoice = None
            item.save(update_fields=["sales_invoice"])
            logger.info(
                f"Sales Quotation Item '{item.id}' detached from invoice "
                f"'{previous_invoice.invoice_number if previous_invoice else 'None'}'."
            )
            return item
        except Exception as e:
            logger.error(f"Error detaching sales quotation item '{item.id}' from invoice: {str(e)}")
            raise
