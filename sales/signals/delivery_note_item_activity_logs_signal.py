# sales/signals/delivery_note_item_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from sales.models.delivery_note_item_model import DeliveryNoteItem


register_crud_signals(
    DeliveryNoteItem,
    actions={
        'create': 'delivery_note_item_created',
        'update': 'delivery_note_item_updated',
        'delete': 'delivery_note_item_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"DeliveryNoteItem '{instance.id if instance else instance.id}' has been "
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'delivery_note_item_id': instance.id,
        'delivery_note_item_name': instance.id if instance else None,
        'created': created,
    }
)