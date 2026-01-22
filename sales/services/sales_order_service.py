from sales.models.sales_order_model import SalesOrder
from sales.models.sales_invoice_model import SalesInvoice
from sales.models.sales_order_item_model import SalesOrderItem
from sales.services.sales_order_item_service import SalesOrderItemService
from django.db import transaction as db_transaction
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from loguru import logger


class SalesOrderService:

    @staticmethod
    @db_transaction.atomic
    def create_sales_order(
        *,
        company,
        branch,
        customer,
        sales_person,
        notes: str | None = None,
        ) -> SalesOrder:
        """
        Create a sales order with optional order items.

        product_list: list of dicts, each dict should have:
            - product: Product instance
            - quantity: int
            - unit_price: float
            - tax_rate: float
        """
        try:
            # Create the order header
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
    def update_sales_order(
        *,
        order: SalesOrder,
        customer=None,
        customer_name: str | None = None,
        sales_person=None,
        notes: str | None = None,
        status: str | None = None,
    ) -> SalesOrder:
        """
        Docstring for update_sales_order
        
        Update a SalesOrder with provided fields.
        Only non-None arguments will be applied.
        1. Update fields on SalesOrder
        2. Recalculate total amount if necessary
        3. Log the update
        4. Return the updated order
        5. Handle exceptions
        """
        try:
            update_fields = []

            if customer is not None:
                order.customer = customer
                update_fields.append("customer")

            if customer_name is not None:
                order.customer_name = customer_name
                update_fields.append("customer_name")

            if sales_person is not None:
                order.sales_person = sales_person
                update_fields.append("sales_person")

            if notes is not None:
                order.notes = notes
                update_fields.append("notes")

            if status is not None:
                order.status = status
                update_fields.append("status")

                if status == SalesOrder.Status.PAID:
                    order.paid_at = timezone.now()
                    update_fields.append("paid_at")

                if status == SalesOrder.Status.DISPATCHED:
                    order.dispatched_at = timezone.now()
                    update_fields.append("dispatched_at")

            if not update_fields:
                return order  # nothing to update

            order.update_total_amount()
            order.save(update_fields=["total_amount", "updated_at"])

            logger.info(f"Sales Order '{order.order_number}' updated: {update_fields}")
            return order

        except Exception as e:
            logger.error(f"Error updating sales order '{order.order_number}': {str(e)}")
            raise

    

    @staticmethod
    @db_transaction.atomic
    def delete_sales_order(order: SalesOrder) -> None:
        """
        Docstring for delete_sales_order
        
        Delete a sales order.
        1. Delete the SalesOrder.
        2. Log the deletion.
        3. Handle exceptions.
        """
        try:
            order_number = order.order_number
            order.delete()
            logger.info(f"Sales Order '{order_number}' deleted.")
        except Exception as e:
            logger.error(f"Error deleting sales order '{order.order_number}': {str(e)}")
            raise


    @staticmethod
    @db_transaction.atomic
    def attach_sales_order_to_invoice(sales_order: SalesOrder, sales_invoice: SalesInvoice) -> SalesOrder:
        """
        Docstring for attach_sales_order_to_invoice
        
        Attach a SalesOrder to a SalesInvoice.
        1. Update SalesInvoice's order field
        2. Log the attachment
        3. Return the updated SalesOrder
        """
        try:
            sales_invoice.order = sales_order
            sales_invoice.save(update_fields=["sales_order"])
            logger.info(f"Sales Order '{sales_order.order_number}' attached to invoice '{sales_invoice.invoice_number}'.")
            return sales_order
        except Exception as e:
            logger.error(f"Error attaching sales order '{sales_order.order_number}' to invoice '{sales_invoice.invoice_number}': {str(e)}")
            raise
    

    @staticmethod
    @db_transaction.atomic
    def update_sales_order_status(order: SalesOrder, new_status: str) -> SalesOrder:
        """
        Update the status of a SalesOrder.
        1. Validate new status
        2. Update status field and timestamps
        3. Log the update
        4. Return the updated order
        5. Handle exceptions
        """
        try:
            new_status = new_status.lower()
            current = order.status

            allowed_transitions = {
                SalesOrder.Status.DRAFT: {
                    SalesOrder.Status.CONFIRMED,
                    SalesOrder.Status.CANCELLED,
                },
                SalesOrder.Status.CONFIRMED: {
                    SalesOrder.Status.PAID,
                    SalesOrder.Status.CANCELLED,
                },
                SalesOrder.Status.PAID: {
                    SalesOrder.Status.DISPATCHED,
                },
                SalesOrder.Status.DISPATCHED: {
                    SalesOrder.Status.COMPLETED,
                },
                SalesOrder.Status.COMPLETED: set(),   # terminal
                SalesOrder.Status.CANCELLED: set(),   # terminal
            }

            if new_status not in SalesOrder.Status.values:
                raise ValueError(f"Invalid status: {new_status}")

            if new_status not in allowed_transitions[current]:
                raise ValueError(
                    f"Illegal status transition: {current} → {new_status}"
                )

            # apply transition
            order.status = new_status
            update_fields = ["status"]

            # timestamps
            if new_status == SalesOrder.Status.PAID:
                order.paid_at = timezone.now()
                update_fields.append("paid_at")

            elif new_status == SalesOrder.Status.DISPATCHED:
                order.dispatched_at = timezone.now()
                update_fields.append("dispatched_at")

            order.save(update_fields=update_fields)

            logger.info(
                f"Sales Order '{order.order_number}' transitioned {current} → {new_status}"
            )
            return order

        except Exception as e:
            logger.error(
                f"Error updating status for sales order '{order.order_number}': {str(e)}"
            )
            raise

