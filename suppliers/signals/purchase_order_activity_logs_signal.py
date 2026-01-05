# suppliers/signals/purchase_order_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from suppliers.models.purchase_order_model import PurchaseOrder


register_crud_signals(
    PurchaseOrder,
    actions={
        'create': 'purchase_order_created',
        'update': 'purchase_order_updated',
        'delete': 'purchase_order_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"PurchaseOrder '{instance.reference_number}' has been"
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'purchase_order_id': instance.id,
        'purchase_order_reference': instance.reference_number,
        'created': created,
    }
)