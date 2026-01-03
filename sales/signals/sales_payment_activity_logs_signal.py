# sales/signals/sales_payment_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from sales.models.sales_payment_model import SalesPayment


register_crud_signals(
    SalesPayment,
    actions={
        'create': 'sales_payment_created',
        'update': 'sales_payment_updated',
        'delete': 'sales_payment_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"SalesPayment '{instance.name}' has been "
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'sales_payment_id': instance.id,
        'sales_payment_name': instance.name,
        'created': created,
    }
)