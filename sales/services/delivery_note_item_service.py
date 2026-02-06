from loguru import logger
from django.db import transaction as db_transaction
from sales.models.delivery_note_model import DeliveryNote
from sales.models.delivery_note_item_model import DeliveryNoteItem


class DeliveryNoteItemService:

    @staticmethod
    @db_transaction.atomic
    def create_delivery_note_item(
        delivery_note,       # DeliveryNote | optional
        product,             # Product
        product_name: str,
        quantity: int,
        unit_price: float,
        tax_rate: float
    ) -> DeliveryNoteItem:
        item = DeliveryNoteItem.objects.create(
            delivery_note=delivery_note,
            product=product,
            product_name=product_name,
            quantity=quantity,
            unit_price=unit_price,
            tax_rate=tax_rate
        )
        
        logger.info(
            f"Delivery Note Item '{item.product_name}' created for note "
            f"'{item.delivery_note.delivery_number if item.delivery_note else 'None'}'."
        )

        # Add/attach to delivery note if provided
        DeliveryNoteItemService.add_to_note(
            item=item,
            note=delivery_note
        ) if delivery_note else None

        return item

    @staticmethod
    @db_transaction.atomic
    def update_delivery_note_item(
        item: DeliveryNoteItem,
        product=None,
        product_name=None,
        quantity=None,
        unit_price=None,
        tax_rate=None,
        delivery_note=None
    ) -> DeliveryNoteItem:
        fields_to_update = []

        if product is not None:
            item.product = product
            fields_to_update.append('product')
        if product_name is not None:
            item.product_name = product_name
            fields_to_update.append('product_name')
        if quantity is not None:
            item.quantity = quantity
            fields_to_update.append('quantity')
        if unit_price is not None:
            item.unit_price = unit_price
            fields_to_update.append('unit_price')
        if tax_rate is not None:
            item.tax_rate = tax_rate
            fields_to_update.append('tax_rate')
        if delivery_note is not None:
            item.delivery_note = delivery_note
            fields_to_update.append('delivery_note')

        item.save(update_fields=fields_to_update)
        logger.info(
            f"Delivery Note Item '{item.product_name}' updated in note "
            f"'{item.delivery_note.delivery_number if item.delivery_note else 'None'}'."
        )
        return item


    @staticmethod
    @db_transaction.atomic
    def delete_delivery_note_item(item: DeliveryNoteItem) -> None:
        note_number = item.delivery_note.delivery_number if item.delivery_note else 'None'
        item_name = item.product_name
        item.delete()
        logger.info(f"Deleted Delivery Note Item '{item_name}' from note '{note_number}'.")


    @staticmethod
    @db_transaction.atomic
    def add_to_note(item: DeliveryNoteItem, note: DeliveryNote) -> DeliveryNoteItem:
        previous_note = item.delivery_note
        item.delivery_note = note
        item.save(update_fields=['delivery_note'])
        if previous_note and previous_note != note:
            previous_note.update_total_amount()
        note.update_total_amount()
        logger.info(
            f"Delivery Note Item '{item.product_name}' attached to note '{note.delivery_number}' "
            f"(previous note: '{previous_note.delivery_number if previous_note else 'None'}')."
        )
        return item


    @staticmethod
    @db_transaction.atomic
    def remove_from_note(item: DeliveryNoteItem) -> DeliveryNoteItem:
        previous_note = item.delivery_note
        item.delivery_note = None
        item.save(update_fields=['delivery_note'])
        if previous_note:
            previous_note.update_total_amount()
        logger.info(
            f"Delivery Note Item '{item.product_name}' detached from note "
            f"'{previous_note.delivery_number if previous_note else 'None'}'."
        )
        return item
