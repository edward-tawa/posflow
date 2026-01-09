# inventory/signals/product_category_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from inventory.models.product_category_model import ProductCategory
from inventory.models.product_model import Product

register_crud_signals(
    ProductCategory,
    actions={
        'create': 'product_category_created',
        'update': 'product_category_updated',
        'delete': 'product_category_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"ProductCategory '{instance.name if instance.name else instance.id}' has been "
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'product_category_id': instance.id,
        'product_category_name': instance.name if instance.name else None,
        'created': created,
    }
)

