# sales/signals/delivery_note_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from sales.models.delivery_note_model import DeliveryNote


register_crud_signals(
    DeliveryNote,
    actions={
        'create': 'delivery_note_created',
        'update': 'delivery_note_updated',
        'delete': 'delivery_note_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"DeliveryNote '{instance.name if instance.name else instance.id}' has been "
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'delivery_note_id': instance.id,
        'delivery_note_name': instance.name if instance.name else None,
        'created': created,
    }
)

