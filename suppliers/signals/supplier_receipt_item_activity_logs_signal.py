# suppliers/signals/supplier_receipt_item_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from suppliers.models.supplier_receipt_item_model import SupplierReceiptItem

register_crud_signals(
    SupplierReceiptItem,
    actions={
        'create': 'supplier_receipt_item_created',
        'update': 'supplier_receipt_item_updated',
        'delete': 'supplier_receipt_item_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"SupplierReceiptItem '{instance.id if instance.id else None}' has been"
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'supplier_receipt_item_id': instance.id,
        'supplier_receipt_item_name': instance.id if instance.id else None,
        'created': created,
    }
)