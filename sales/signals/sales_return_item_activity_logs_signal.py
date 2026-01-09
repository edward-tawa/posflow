# sales/signals/sales_return_item_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from sales.models.sales_return_item_model import SalesReturnItem


register_crud_signals(
    SalesReturnItem,
    actions={
        'create': 'sales_return_item_created',
        'update': 'sales_return_item_updated',
        'delete': 'sales_return_item_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"SalesReturnItem '{instance.id if instance.id else instance.id}' has been "
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'sales_return_item_id': instance.id,
        'sales_return_item_name': instance.id if instance.id else None,
        'created': created,
    }
)