# suppliers/signals/purchase_order_item_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from suppliers.models.purchase_order_item_model import PurchaseOrderItem


register_crud_signals(
    PurchaseOrderItem,
    actions={
        'create': 'purchase_order_item_created',
        'update': 'purchase_order_item_updated',
        'delete': 'purchase_order_item_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"PurchaseOrderItem '{instance.purchase_order.reference_number}' has been"
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'purchase_order_item_id': instance.id,
        # 'purchase_order_item_name': instance.name,
        'created': created,
    }
)