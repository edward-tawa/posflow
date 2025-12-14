from loguru import logger
from django.db import transaction as db_transaction
from sales.models.delivery_note_model import DeliveryNote
from sales.models.delivery_note_item_model import DeliveryNoteItem
from sales.models.sales_order_model import SalesOrder
from sales.models.sales_receipt_model import SalesReceipt


class DeliveryNoteService:

    @staticmethod
    @db_transaction.atomic
    def create_delivery_note(**kwargs) -> DeliveryNote:
        try:
            note = DeliveryNote.objects.create(**kwargs)
            logger.info(f"Delivery Note '{note.delivery_number}' created for company '{note.company.name}'.")
            return note
        except Exception as e:
            logger.error(f"Error creating delivery note: {str(e)}")
            raise

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
        previous_order = note.sales_order
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

    # -----------------------------
    # DeliveryNoteItem Methods
    # -----------------------------

    @staticmethod
    @db_transaction.atomic
    def create_item(**kwargs) -> DeliveryNoteItem:
        try:
            item = DeliveryNoteItem.objects.create(**kwargs)
            logger.info(f"Delivery Note Item '{item.product_name}' added to note '{item.delivery_note.delivery_number}'.")
            return item
        except Exception as e:
            logger.error(f"Error creating delivery note item: {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def update_item(item: DeliveryNoteItem, **kwargs) -> DeliveryNoteItem:
        try:
            for key, value in kwargs.items():
                setattr(item, key, value)
            item.save(update_fields=kwargs.keys())
            logger.info(f"Delivery Note Item '{item.product_name}' updated in note '{item.delivery_note.delivery_number}'.")
            return item
        except Exception as e:
            logger.error(f"Error updating delivery note item '{item.product_name}': {str(e)}")
            raise

    @staticmethod
    @db_transaction.atomic
    def delete_item(item: DeliveryNoteItem) -> None:
        item_name = item.product_name
        note_number = item.delivery_note.delivery_number
        item.delete()
        logger.info(f"Deleted Delivery Note Item '{item_name}' from note '{note_number}'.")

    @staticmethod
    @db_transaction.atomic
    def move_item_to_another_note(item: DeliveryNoteItem, new_note: DeliveryNote) -> DeliveryNoteItem:
        previous_note = item.delivery_note
        item.delivery_note = new_note
        item.save(update_fields=['delivery_note'])
        # Update totals for both notes
        if previous_note != new_note:
            previous_note.update_total_amount()
            new_note.update_total_amount()
        logger.info(
            f"Delivery Note Item '{item.product_name}' moved from note '{previous_note.delivery_number}' to note '{new_note.delivery_number}'."
        )
        return item
