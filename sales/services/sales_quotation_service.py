from sales.models.sales_quotation_model import SalesQuotation
from sales.services.sales_quotation_item_service import SalesQuotationItemService
from customers.models.customer_model import Customer
from django.db import transaction as db_transaction
from loguru import logger


class SalesQuotationService:
    # Sales Quotation Management Service
    @staticmethod
    @db_transaction.atomic
    def create_sales_quotation(
        company,
        branch,
        customer,
        valid_until,
        created_by,
        notes: str = None,
        status: str = "draft",
        products: list = None
    ) -> SalesQuotation:
        """
        Docstring for create_sales_quotation
        Create a sales quotation.
        1. Create SalesQuotation
        2. Log the creation
        3. Return the created quotation
        """
        try:
            sales_quotation = SalesQuotation.objects.create(
                company=company,
                branch=branch,
                customer=customer,
                valid_until=valid_until,
                created_by=created_by,
                notes=notes,
                status=status,
            )

            logger.info(
                f"Sales Quotation '{sales_quotation.quotation_number}' (ID {sales_quotation.id}) created for company '{sales_quotation.company.name}'."
            )
            for product in products or []:
                item = SalesQuotationItemService.create_sales_quotation_item(
                    sales_quotation=sales_quotation,
                    product_name=product.get("product_name"),
                    quantity=product.get("quantity"),
                    unit_price=product.get("unit_price"),
                    tax_rate=product.get("tax_rate"),
                    sales_invoice=product.get("sales_invoice"),
                )
                SalesQuotationItemService.add_quotation_item_to_quotation(
                    sales_quotation=sales_quotation,
                    item=item
                )
            return sales_quotation

        except Exception as e:
            logger.error(f"Error creating sales quotation: {str(e)}")
            raise


    @staticmethod
    @db_transaction.atomic
    def update_sales_quotation(
        quotation: SalesQuotation,
        customer: Customer = None,
        valid_until = None,
        status: str = None,
        notes: str = None,
        branch = None,
        company = None,
        created_by = None,
    ) -> SalesQuotation:
        """
        Docstring for update_sales_quotation
        Update a SalesQuotation with provided fields.
        Only non-None arguments will be applied.
        1. Update fields on SalesQuotation
        2. Log the update
        3. Return the updated quotation
        """
        try:
            update_fields = []

            if customer is not None:
                quotation.customer = customer
                update_fields.append("customer")

            if valid_until is not None:
                quotation.valid_until = valid_until
                update_fields.append("valid_until")

            if status is not None:
                if status not in dict(SalesQuotation.STATUS_CHOICES):
                    raise ValueError(f"Invalid status: {status}")
                quotation.status = status
                update_fields.append("status")

            if notes is not None:
                quotation.notes = notes
                update_fields.append("notes")

            if branch is not None:
                quotation.branch = branch
                update_fields.append("branch")

            if company is not None:
                quotation.company = company
                update_fields.append("company")

            if created_by is not None:
                quotation.created_by = created_by
                update_fields.append("created_by")

            if update_fields:
                quotation.save(update_fields=update_fields)
                logger.info(
                    f"Sales Quotation '{quotation.quotation_number}' updated: {update_fields}"
                )
            
            quotation.update_total_amount()

            return quotation

        except Exception as e:
            logger.error(f"Error updating sales quotation '{quotation.quotation_number}': {str(e)}")
            raise


    @staticmethod
    @db_transaction.atomic
    def delete_sales_quotation(quotation: SalesQuotation) -> None:
        """
        Docstring for delete_sales_quotation
        Delete a sales quotation.
        1. Delete the SalesQuotation.
        2. Log the deletion.
        3. Handle exceptions.
        """
        try:
            quotation_number = quotation.quotation_number
            quotation_id = quotation.id
            quotation.delete()
            logger.info(f"Sales Quotation '{quotation_number}' (ID {quotation_id}) deleted.")
        except Exception as e:
            logger.error(f"Error deleting sales quotation '{quotation_number}': {str(e)}")
            raise


    @staticmethod
    @db_transaction.atomic
    def update_sales_quotation_status(
        quotation: SalesQuotation,
        new_status: str
    ) -> SalesQuotation:
        """
        Docstring for update_sales_quotation_status
        
        Update the status of a SalesQuotation.
        1. Validate new status
        2. Update status field
        3. Log the update
        4. Return the updated quotation
        5. Handle exceptions
        """
        if new_status not in dict(SalesQuotation.STATUS_CHOICES):
            raise ValueError(f"Invalid status: {new_status}")

        try:
            quotation.status = new_status
            quotation.save(update_fields=["status"])
            logger.info(
                f"Sales Quotation '{quotation.quotation_number}' status updated to '{new_status}'."
            )
            return quotation

        except Exception as e:
            logger.error(f"Error updating status for sales quotation '{quotation.quotation_number}': {str(e)}")
            raise


    @staticmethod
    @db_transaction.atomic
    def attach_to_customer(
        quotation: SalesQuotation,
        customer: Customer
    ) -> SalesQuotation:
        try:
            previous_customer = quotation.customer
            quotation.customer = customer
            quotation.save(update_fields=["customer"])

            logger.info(
                f"Sales Quotation '{quotation.quotation_number}' attached to customer "
                f"'{customer.name}' (was '{previous_customer.name if previous_customer else 'None'}')."
            )
            return quotation

        except Exception as e:
            logger.error(
                f"Error attaching sales quotation '{quotation.quotation_number}' to customer '{customer.name}': {str(e)}"
            )
            raise


    @staticmethod
    @db_transaction.atomic
    def detach_from_customer(
        quotation: SalesQuotation
    ) -> SalesQuotation:
        """
        Docstring for detach_from_customer
        
        Detach a SalesQuotation from its customer.
        1. Update the customer field to None
        2. Log the detachment
        3. Return the updated quotation
        4. Handle exceptions
        """
        try:
            previous_customer = quotation.customer
            quotation.customer = None
            quotation.save(update_fields=["customer"])

            logger.info(
                f"Sales Quotation '{quotation.quotation_number}' detached from customer "
                f"'{previous_customer.name if previous_customer else 'None'}'."
            )
            return quotation

        except Exception as e:
            logger.error(
                f"Error detaching sales quotation '{quotation.quotation_number}' from customer: {str(e)}"
            )
            raise
