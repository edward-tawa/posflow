# inventory/signals/stock_movement_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from inventory.models.stock_movement_model import StockMovement


register_crud_signals(
    StockMovement,
    actions={
        'create': 'stock_movement_created',
        'update': 'stock_movement_updated',
        'delete': 'stock_movement_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"StockMovement '{instance.name if instance.name else instance.id}' has been "
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'stock_movement_id': instance.id,
        'stock_movement_name': instance.name if instance.name else None,
        'created': created,
    }
)

