# inventory/signals/product_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from inventory.models.product_model import Product

register_crud_signals(
    Product,
    actions={
        'create': 'product_created',
        'update': 'product_updated',
        'delete': 'product_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"Product '{instance.name}' has been "
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'product_id': instance.id,
        'product_name': instance.name,
        'created': created,
    }
)

