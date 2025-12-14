from sales.models.sales_quotation_model import SalesQuotation
from customers.models.customer_model import Customer
from django.db import transaction as db_transaction
from loguru import logger


class SalesQuotationService:

    @staticmethod
    @db_transaction.atomic
    def create_sales_quotation(**kwargs) -> SalesQuotation:
        try:
            quotation = SalesQuotation.objects.create(**kwargs)
            logger.info(
                f"Sales Quotation '{quotation.quotation_number}' (ID {quotation.id}) created for company '{quotation.company.name}'."
            )
            return quotation
        except Exception as e:
            logger.error(f"Error creating sales quotation: {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def update_sales_quotation(quotation: SalesQuotation, **kwargs) -> SalesQuotation:
        try:
            for key, value in kwargs.items():
                setattr(quotation, key, value)
            quotation.save(update_fields=kwargs.keys())
            logger.info(f"Sales Quotation '{quotation.quotation_number}' (ID {quotation.id}) updated.")
            return quotation
        except Exception as e:
            logger.error(f"Error updating sales quotation '{quotation.quotation_number}': {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def delete_sales_quotation(quotation: SalesQuotation) -> None:
        try:
            quotation_number = quotation.quotation_number
            quotation_id = quotation.id
            quotation.delete()
            logger.info(f"Sales Quotation '{quotation_number}' (ID {quotation_id}) deleted.")
        except Exception as e:
            logger.error(f"Error deleting sales quotation '{quotation.quotation_number}': {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def update_sales_quotation_status(quotation: SalesQuotation, new_status: str) -> SalesQuotation:
        if new_status not in dict(SalesQuotation.STATUS_CHOICES):
            raise ValueError(f"Invalid status: {new_status}")
        try:
            quotation.status = new_status
            quotation.save(update_fields=["status"])
            logger.info(f"Sales Quotation '{quotation.quotation_number}' (ID {quotation.id}) status updated to '{new_status}'.")
            return quotation
        except Exception as e:
            logger.error(f"Error updating status for sales quotation '{quotation.quotation_number}': {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def attach_to_customer(quotation: SalesQuotation, customer: Customer) -> SalesQuotation:
        try:
            previous_customer = quotation.customer
            quotation.customer = customer
            quotation.save(update_fields=["customer"])
            logger.info(
                f"Sales Quotation '{quotation.quotation_number}' (ID {quotation.id}) attached to customer "
                f"'{customer.name}' (was '{previous_customer.name if previous_customer else 'None'}')."
            )
            return quotation
        except Exception as e:
            logger.error(f"Error attaching sales quotation '{quotation.quotation_number}' to customer '{customer.name}': {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def detach_from_customer(quotation: SalesQuotation) -> SalesQuotation:
        try:
            previous_customer = quotation.customer
            quotation.customer = None
            quotation.save(update_fields=["customer"])
            logger.info(
                f"Sales Quotation '{quotation.quotation_number}' (ID {quotation.id}) detached from customer "
                f"'{previous_customer.name if previous_customer else 'None'}'."
            )
            return quotation
        except Exception as e:
            logger.error(f"Error detaching sales quotation '{quotation.quotation_number}' from customer: {str(e)}")
            raise
