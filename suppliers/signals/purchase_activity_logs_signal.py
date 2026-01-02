# suppliers/signals/purchase_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from suppliers.models.purchase_model import Purchase


register_crud_signals(
    Purchase,
    actions={
        'create': 'purchase_created',
        'update': 'purchase_updated',
        'delete': 'purchase_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"Purchase '{instance.name}' has been"
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'purchase_id': instance.id,
        'purchase_name': instance.name,
        'created': created,
    }
)