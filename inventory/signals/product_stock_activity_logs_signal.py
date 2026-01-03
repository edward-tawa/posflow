# inventory/signals/product_stock_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from inventory.models.product_stock_model import ProductStock
from inventory.models.product_model import Product

register_crud_signals(
    ProductStock,
    actions={
        'create': 'product_stock_created',
        'update': 'product_stock_updated',
        'delete': 'product_stock_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"ProductStock '{instance.name}' has been "
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'product_stock_id': instance.id,
        'product_stock_name': instance.name,
        'created': created,
    }
)

