# sales/signals/sales_return_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from sales.models.sales_return_model import SalesReturn


register_crud_signals(
    SalesReturn,
    actions={
        'create': 'sales_return_created',
        'update': 'sales_return_updated',
        'delete': 'sales_return_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"SalesReturn '{instance.return_number if instance else instance.id}' has been "
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'sales_return_id': instance.id,
        'sales_return_name': instance.return_number if instance else None,
        'created': created,
    }
)