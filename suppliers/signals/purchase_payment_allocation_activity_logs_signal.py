# suppliers/signals/purchase_payment_allocation_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from suppliers.models.purchase_payment_allocation_model import PurchasePaymentAllocation


register_crud_signals(
    PurchasePaymentAllocation,
    actions={
        'create': 'purchase_payment_allocation_created',
        'update': 'purchase_payment_allocation_updated',
        'delete': 'purchase_payment_allocation_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"PurchasePaymentAllocation '{instance.name}' has been"
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'purchase_payment_allocation_id': instance.id,
        'purchase_payment_allocation_name': instance.name,
        'created': created,
    }
)