from loguru import logger
from django.db import transaction as db_transaction
from sales.models.delivery_note_model import DeliveryNote
from sales.models.delivery_note_item_model import DeliveryNoteItem
from sales.services.delivery_note_item_service import DeliveryNoteItemService
from sales.models.sales_order_model import SalesOrder
from sales.models.sales_receipt_model import SalesReceipt



class DeliveryNoteService:

    @staticmethod
    @db_transaction.atomic
    def create_delivery_note(
        company,
        branch,
        customer,
        sales_order,
        product_list=None,
        issued_by=None,
        notes=None,
        status='pending'
    ) -> DeliveryNote:
        try:
            note = DeliveryNote.objects.create(
                company=company,
                branch=branch,
                customer=customer,
                sales_order=sales_order,
                issued_by=issued_by,
                notes=notes,
                status=status
            )
            logger.info(f"Delivery Note '{note.delivery_number}' created for company '{note.company.name}'.")
            for product in product_list:
                delivery_note_item = DeliveryNoteItemService.create_delivery_note_item(
                    delivery_note=note,
                    product=None,
                    product_name="Sample Item",
                    quantity=1,
                    unit_price=0.0,
                    tax_rate=0.0
                )
                DeliveryNoteItemService.add_to_note(
                    item=delivery_note_item,
                    note=note
                )


            
            return note
        except Exception as e:
            logger.error(f"Error creating delivery note: {str(e)}")
            raise
    @staticmethod
    @db_transaction.atomic
    def update_delivery_note(
        note: DeliveryNote,
        customer=None,
        sales_order=None,
        issued_by=None,
        notes=None,
        status=None
    ) -> DeliveryNote:
        fields_to_update = []

        if customer is not None:
            note.customer = customer
            fields_to_update.append('customer')
        if sales_order is not None:
            note.sales_order = sales_order
            fields_to_update.append('sales_order')
        if issued_by is not None:
            note.issued_by = issued_by
            fields_to_update.append('issued_by')
        if notes is not None:
            note.notes = notes
            fields_to_update.append('notes')
        if status is not None:
            note.status = status
            fields_to_update.append('status')

        note.save(update_fields=fields_to_update)
        logger.info(f"Delivery Note '{note.delivery_number}' updated.")
        return note

    @staticmethod
    @db_transaction.atomic
    def update_delivery_note_status(note: DeliveryNote, new_status: str) -> DeliveryNote:
        if new_status not in dict(DeliveryNote.STATUS_CHOICES):
            raise ValueError(f"Invalid status: {new_status}")
        note.status = new_status
        note.save(update_fields=['status'])
        logger.info(f"Delivery Note '{note.delivery_number}' status updated to '{new_status}'.")
        return note

    @staticmethod
    @db_transaction.atomic
    def delete_delivery_note(note: DeliveryNote) -> None:
        note_number = note.delivery_number
        note.delete()
        logger.info(f"Delivery Note '{note_number}' deleted.")

    @staticmethod
    @db_transaction.atomic
    def attach_to_sales_order(note: DeliveryNote, order: SalesOrder) -> DeliveryNote:
        note.sales_order = order
        note.save(update_fields=['sales_order'])
        logger.info(f"Delivery Note '{note.delivery_number}' attached to Sales Order '{order.order_number}'.")
        return note

    @staticmethod
    @db_transaction.atomic
    def attach_to_sales_receipt(note: DeliveryNote, receipt: SalesReceipt) -> DeliveryNote:
        note.sales_receipt = receipt
        note.save(update_fields=['sales_receipt'])
        logger.info(f"Delivery Note '{note.delivery_number}' attached to Sales Receipt '{receipt.receipt_number}'.")
        return note

    @staticmethod
    @db_transaction.atomic
    def detach_from_sales_receipt(note: DeliveryNote) -> DeliveryNote:
        previous = note.sales_receipt
        note.sales_receipt = None
        note.save(update_fields=['sales_receipt'])
        logger.info(
            f"Delivery Note '{note.delivery_number}' detached from Sales Receipt "
            f"'{previous.receipt_number if previous else 'None'}'."
        )
        return note