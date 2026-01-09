# inventory/signals/stock_take__item_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from inventory.models.stock_take_item_model import StockTakeItem


register_crud_signals(
    StockTakeItem,
    actions={
        'create': 'stock_take_item_created',
        'update': 'stock_take_item_updated',
        'delete': 'stock_take_item_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"StockTakeItem '{instance.name if instance.name else instance.id}' has been "
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'stock_take_item_id': instance.id,
        'stock_take_item_name': instance.name if instance.name else None,
        'created': created,
    }
)

