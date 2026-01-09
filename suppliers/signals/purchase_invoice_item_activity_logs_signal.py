# suppliers/signals/purchase_invoice_item_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from suppliers.models.purchase_invoice_item_model import PurchaseInvoiceItem


register_crud_signals(
    PurchaseInvoiceItem,
    actions={
        'create': 'purchase_invoice_item_created',
        'update': 'purchase_invoice_item_updated',
        'delete': 'purchase_invoice_item_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"PurchaseInvoiceItem '{instance.id}' has been"
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'purchase_invoice_item_id': instance.id,
        'purchase_invoice_item_name': instance.id if instance.id else None,
        'created': created,
    }
)