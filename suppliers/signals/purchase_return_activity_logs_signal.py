# suppliers/signals/purchase_return_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from suppliers.models.purchase_return_model import PurchaseReturn

register_crud_signals(
    PurchaseReturn,
    actions={
        'create': 'purchase_return_created',
        'update': 'purchase_return_updated',
        'delete': 'purchase_return_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"PurchaseReturn '{instance.name if instance.name else None}' has been"
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'purchase_return_id': instance.id,
        'purchase_return_name': instance.name if instance.name else None,
        'created': created,
    }
)