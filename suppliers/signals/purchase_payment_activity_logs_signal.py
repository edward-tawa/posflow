# suppliers/signals/purchase_payment_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from suppliers.models.purchase_payment_model import PurchasePayment


register_crud_signals(
    PurchasePayment,
    actions={
        'create': 'purchase_payment_created',
        'update': 'purchase_payment_updated',
        'delete': 'purchase_payment_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"PurchasePayment '{instance.name}' has been"
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'purchase_payment_id': instance.id,
        'purchase_payment_name': instance.name,
        'created': created,
    }
)