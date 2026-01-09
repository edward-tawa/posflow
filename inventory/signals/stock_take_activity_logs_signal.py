# inventory/signals/stock_take_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from inventory.models.stock_take_model import StockTake


register_crud_signals(
    StockTake,
    actions={
        'create': 'stock_take_created',
        'update': 'stock_take_updated',
        'delete': 'stock_take_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"StockTake '{instance.name if instance.name else instance.id}' has been "
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'stock_take_id': instance.id,
        'stock_take_name': instance.name if instance.name else None,
        'created': created,
    }
)

