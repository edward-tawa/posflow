# customer/signals/customer_activity_logs_signal.py
from customers.models.customer_model import Customer
from config.activity_log.crud_registry import register_crud_signals

register_crud_signals(
    Customer,
    actions={
        'create': 'customer_created',
        'update': 'customer_updated',
        'delete': 'customer_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"Customer '{instance.name}' has been "
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'customer_id': instance.id,
        'customer_name': instance.name,
        'created': created,
    }
)

