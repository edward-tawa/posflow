# sales/signals/sales_receipt_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from sales.models.sales_receipt_model import SalesReceipt


register_crud_signals(
    SalesReceipt,
    actions={
        'create': 'sales_receipt_created',
        'update': 'sales_receipt_updated',
        'delete': 'sales_receipt_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"SalesReceipt '{instance.name}' has been "
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'sales_receipt_id': instance.id,
        'sales_receipt_name': instance.name,
        'created': created,
    }
)