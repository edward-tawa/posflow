from loguru import logger
from sales.models.sale_model import Sale
from django.db import transaction as db_transaction


# To be revisited to see where ochestration will be conducted from.

class SaleService:

    @staticmethod
    @db_transaction.atomic
    def create_sale(
        company,
        branch,
        customer,
        sale_type='CASH',
        sales_invoice=None,
        sale_receipt=None,
        issued_by=None,
        notes=None
    ) -> Sale:
        try:
            sale = Sale.objects.create(
                company=company,
                branch=branch,
                customer=customer,
                sale_type=sale_type,
                sales_invoice=sales_invoice,
                sale_receipt=sale_receipt,
                issued_by=issued_by,
                notes=notes
            )
            logger.info(f"Sale '{sale.sale_number}' created for company '{sale.company.name}'.")
            return sale
        except Exception as e:
            logger.error(f"Error creating sale: {str(e)}")
            raise

    

    # To be edited below as needed for total amounts
    @staticmethod
    @db_transaction.atomic
    def update_sale(
        sale: Sale,
        customer=None,
        sale_type: str | None = None,
        sales_invoice=None,
        sale_receipt=None,
        issued_by=None,
        notes: str | None = None
    ) -> Sale:
        try:
            if customer is not None:
                sale.customer = customer
            if sale_type is not None:
                sale.sale_type = sale_type
            if sales_invoice is not None:
                sale.sales_invoice = sales_invoice
            if sale_receipt is not None:
                sale.sale_receipt = sale_receipt
            if issued_by is not None:
                sale.issued_by = issued_by
            if notes is not None:
                sale.notes = notes
            sale.save()
            logger.info(f"Sale '{sale.sale_number}' updated.")
            return sale
        except Exception as e:
            logger.error(f"Error updating sale '{sale.sale_number}': {str(e)}")
            raise


    

    
    @staticmethod
    @db_transaction.atomic
    def update_payment_status(sale: Sale) -> None:
        if sale.sales_receipt:
            total_paid = sum([item.amount for item in sale.sales_receipt.items.all()])
        else:
            total_paid = 0

        if total_paid >= sale.total_amount:
            sale.payment_status = 'FULLY_PAID'
        elif total_paid > 0:
            sale.payment_status = 'PARTIALLY_PAID'
        else:
            sale.payment_status = 'UNPAID'

        sale.save()
        logger.info(f"Updated payment status for Sale '{sale.sale_number}' to {sale.payment_status}")

    


    @staticmethod
    @db_transaction.atomic
    def mark_as_paid(sale: Sale, receipt=None) -> None:
        if receipt:
            sale.sales_receipt = receipt
        sale.payment_status = 'FULLY_PAID'
        sale.save()
        logger.info(f"Sale '{sale.sale_number}' marked as fully paid.")



    @staticmethod
    @db_transaction.atomic
    def get_sales_by_customer(customer_id):
        return Sale.objects.filter(customer_id=customer_id).select_related(
            'company', 'branch', 'customer', 'issued_by'
        )

    @staticmethod
    @db_transaction.atomic
    def get_sales_by_branch(branch_id):
        return Sale.objects.filter(branch_id=branch_id).select_related(
            'company', 'branch', 'customer', 'issued_by'
        )
    
    
    @staticmethod
    @db_transaction.atomic
    def cancel_sale(sale: Sale):
        # Example: soft-delete pattern
        sale.notes = (sale.notes or "") + "\nSale cancelled."
        sale.total_amount = 0
        sale.payment_status = 'UNPAID'
        sale.save()
        logger.info(f"Sale '{sale.sale_number}' cancelled.")




