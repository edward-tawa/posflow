# suppliers/signals/supplier_receipt_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from suppliers.models.supplier_receipt_model import SupplierReceipt

register_crud_signals(
    SupplierReceipt,
    actions={
        'create': 'supplier_receipt_created',
        'update': 'supplier_receipt_updated',
        'delete': 'supplier_receipt_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"SupplierReceipt '{instance.id if instance.id else None}' has been"
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'supplier_receipt_id': instance.id,
        'supplier_receipt_name': instance.id if instance.id else None,
        'created': created,
    }
)