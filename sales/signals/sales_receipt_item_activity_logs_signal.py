# sales/signals/sales_receipt_item_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from sales.models.sales_receipt_item_model import SalesReceiptItem


register_crud_signals(
    SalesReceiptItem,
    actions={
        'create': 'sales_receipt_item_created',
        'update': 'sales_receipt_item_updated',
        'delete': 'sales_receipt_item_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"SalesReceiptItem '{instance.id if instance.id else instance.id}' has been "
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'sales_receipt_item_id': instance.id,
        'sales_receipt_item_name': instance.id if instance.id else None,
        'created': created,
    }
)