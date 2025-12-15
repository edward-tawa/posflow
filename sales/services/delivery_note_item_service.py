from loguru import logger
from django.db import transaction as db_transaction
from sales.models.delivery_note_model import DeliveryNote
from sales.models.delivery_note_item_model import DeliveryNoteItem


class DeliveryNoteItemService:

    @staticmethod
    @db_transaction.atomic
    def create_item(**kwargs) -> DeliveryNoteItem:
        item = DeliveryNoteItem.objects.create(**kwargs)
        logger.info(f"Delivery Note Item '{item.product_name}' created for note '{item.delivery_note.delivery_number if item.delivery_note else 'None'}'.")
        return item

    @staticmethod
    @db_transaction.atomic
    def update_item(item: DeliveryNoteItem, **kwargs) -> DeliveryNoteItem:
        for key, value in kwargs.items():
            setattr(item, key, value)
        item.save(update_fields=kwargs.keys())
        logger.info(f"Delivery Note Item '{item.product_name}' updated in note '{item.delivery_note.delivery_number if item.delivery_note else 'None'}'.")
        return item

    @staticmethod
    @db_transaction.atomic
    def delete_item(item: DeliveryNoteItem) -> None:
        note_number = item.delivery_note.delivery_number if item.delivery_note else 'None'
        item_name = item.product_name
        item.delete()
        logger.info(f"Deleted Delivery Note Item '{item_name}' from note '{note_number}'.")

    @staticmethod
    @db_transaction.atomic
    def attach_to_note(item: DeliveryNoteItem, note: DeliveryNote) -> DeliveryNoteItem:
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
    def detach_from_note(item: DeliveryNoteItem) -> DeliveryNoteItem:
        previous_note = item.delivery_note
        item.delivery_note = None
        item.save(update_fields=['delivery_note'])
        if previous_note:
            previous_note.update_total_amount()
        logger.info(f"Delivery Note Item '{item.product_name}' detached from note '{previous_note.delivery_number if previous_note else 'None'}'.")
        return item
    


    @action(detail=True, methods=['post'], url_path='attach')
    def attach(self, request, pk=None):
        item = self.get_object()
        note_id = request.data.get("note_id")
        if not note_id:
            return Response({"detail": "note_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            note = DeliveryNote.objects.get(id=note_id)
            updated_item = DeliveryNoteItemService.attach_to_note(item, note)
            serializer = self.get_serializer(updated_item)
            return Response(serializer.data)
        except DeliveryNote.DoesNotExist:
            return Response({"detail": "Delivery Note not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error attaching item to note: {str(e)}")
            return Response({"detail": "Error attaching item."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='detach')
    def detach(self, request, pk=None):
        item = self.get_object()
        try:
            updated_item = DeliveryNoteItemService.detach_from_note(item)
            serializer = self.get_serializer(updated_item)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error detaching item from note: {str(e)}")
            return Response({"detail": "Error detaching item."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
