# suppliers/signals/purchase_invoice_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from suppliers.models.purchase_invoice_model import PurchaseInvoice


register_crud_signals(
    PurchaseInvoice,
    actions={
        'create': 'purchase_invoice_created',
        'update': 'purchase_invoice_updated',
        'delete': 'purchase_invoice_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"PurchaseInvoice '{instance.name}' has been"
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'purchase_invoice_id': instance.id,
        'purchase_invoice_name': instance.name,
        'created': created,
    }
)