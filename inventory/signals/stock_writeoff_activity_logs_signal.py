# inventory/signals/stock_writeoff_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from inventory.models.stock_writeoff_model import StockWriteOff

register_crud_signals(
    StockWriteOff,
    actions={
        'create': 'stock_writeoff_created',
        'update': 'stock_writeoff_updated',
        'delete': 'stock_writeoff_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"StockWriteOff '{instance.name}' has been "
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'stock_writeoff_id': instance.id,
        'stock_writeoff_name': instance.name,
        'created': created,
    }
)

