from sales.models.sales_order_model import SalesOrder
from sales.models.sales_invoice_model import SalesInvoice
from sales.models.sales_order_item_model import SalesOrderItem  # assume you have this model
from django.db import transaction as db_transaction
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from loguru import logger


class SalesOrderService:

    @staticmethod
    @db_transaction.atomic
    def create_sales_order(*,company,branch,customer,sales_person,notes: str | None = None) -> SalesOrder:
        try:
            sales_order = SalesOrder.objects.create(
                company=company,
                branch=branch,
                customer=customer,
                sales_person=sales_person,
                notes=notes
            )
            logger.info(f"Sales Order '{sales_order.order_number}' created for company '{sales_order.company.name}'.")
            return sales_order
        except Exception as e:
            logger.error(f"Error creating sales order: {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def update_sales_order(order: SalesOrder, **kwargs) -> SalesOrder:
        try:
            for key, value in kwargs.items():
                setattr(order, key, value)
            order.save(update_fields=kwargs.keys())
            logger.info(f"Sales Order '{order.order_number}' updated.")
            return order
        except Exception as e:
            logger.error(f"Error updating sales order '{order.order_number}': {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def delete_sales_order(order: SalesOrder) -> None:
        try:
            order_number = order.order_number
            order.delete()
            logger.info(f"Sales Order '{order_number}' deleted.")
        except Exception as e:
            logger.error(f"Error deleting sales order '{order.order_number}': {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def attach_to_invoice(order: SalesOrder, invoice: SalesInvoice) -> SalesOrder:
        try:
            order.sales_invoice = invoice
            order.save(update_fields=["sales_invoice"])
            logger.info(f"Sales Order '{order.order_number}' attached to invoice '{invoice.invoice_number}'.")
            return order
        except Exception as e:
            logger.error(f"Error attaching sales order '{order.order_number}' to invoice '{invoice.invoice_number}': {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def update_sales_order_status(order: SalesOrder, new_status: str) -> SalesOrder:
        try:
            order.status = new_status
            # automatically update timestamps for certain statuses
            if new_status.upper() == 'PAID':
                order.paid_at = timezone.now()
            elif new_status.upper() == 'DISPATCHED':
                order.dispatched_at = timezone.now()
            order.save(update_fields=['status', 'paid_at', 'dispatched_at'])
            logger.info(f"Sales Order '{order.order_number}' status updated to '{new_status}'.")
            return order
        except Exception as e:
            logger.error(f"Error updating status for sales order '{order.order_number}': {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def recalc_order_total(order: SalesOrder) -> SalesOrder:
        try:
            total = sum(item.total_price for item in order.items.all())
            order.total_amount = float(Decimal(total).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            order.save(update_fields=['total_amount'])
            logger.info(f"Recalculated total for Sales Order '{order.order_number}' to {order.total_amount}")
            return order
        except Exception as e:
            logger.error(f"Error recalculating total for sales order '{order.order_number}': {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def mark_as_paid(order: SalesOrder) -> SalesOrder:
        order.status = 'PAID'
        order.paid_at = timezone.now()
        order.save(update_fields=['status', 'paid_at'])
        logger.info(f"Marked Sales Order '{order.order_number}' as PAID.")
        return order

    @staticmethod
    @db_transaction.atomic
    def bulk_create_order_items(order: SalesOrder, items_data: list) -> list:
        """
        Bulk create SalesOrderItems for the given order and recalc total.
        """
        try:
            items = [SalesOrderItem(order=order, **data) for data in items_data]
            created_items = SalesOrderItem.objects.bulk_create(items)
            logger.info(f"Bulk created {len(created_items)} items for Sales Order '{order.order_number}'")
            # recalc order total after bulk creation
            SalesOrderService.recalc_order_total(order)
            return created_items
        except Exception as e:
            logger.error(f"Error bulk creating items for sales order '{order.order_number}': {str(e)}")
            raise
