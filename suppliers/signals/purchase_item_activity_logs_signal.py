# suppliers/signals/purchase_item_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from suppliers.models.purchase_item_model import PurchaseItem


register_crud_signals(
    PurchaseItem,
    actions={
        'create': 'purchase_item_created',
        'update': 'purchase_item_updated',
        'delete': 'purchase_item_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"PurchaseItem '{instance.id if instance.id else None}' has been"
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'purchase_item_id': instance.id,
        'purchase_item_name': instance.id if instance.id else None,
        'created': created,
    }
)