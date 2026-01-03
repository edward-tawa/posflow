# suppliers/signals/purchase_return_item_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from suppliers.models.purchase_return_item_model import PurchaseReturnItem

register_crud_signals(
    PurchaseReturnItem,
    actions={
        'create': 'purchase_return_item_created',
        'update': 'purchase_return_item_updated',
        'delete': 'purchase_return_item_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"PurchaseReturnItem '{instance.name}' has been"
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'purchase_return_item_id': instance.id,
        'purchase_return_item_name': instance.name,
        'created': created,
    }
)