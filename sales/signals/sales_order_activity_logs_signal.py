# sales/signals/sales_order_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from sales.models.sales_order_model import SalesOrder


register_crud_signals(
    SalesOrder,
    actions={
        'create': 'sales_order_created',
        'update': 'sales_order_updated',
        'delete': 'sales_order_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"SalesOrder '{instance.name}' has been "
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'sales_order_id': instance.id,
        'sales_order_name': instance.name,
        'created': created,
    }
)