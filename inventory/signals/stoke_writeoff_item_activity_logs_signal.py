# inventory/signals/stock_writeoff_item_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from inventory.models.stock_writeoff_item_model import StockWriteOffItem


register_crud_signals(
    StockWriteOffItem,
    actions={
        'create': 'stock_writeoff_item_created',
        'update': 'stock_writeoff_item_updated',
        'delete': 'stock_writeoff_item_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"StockWriteOffItem '{instance.name if instance.name else instance.id}' has been"
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'stock_writeoff_item_id': instance.id,
        'stock_writeoff_item_name': instance.name if instance.name else None,
        'created': created,
    }
)

