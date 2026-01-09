# sales/signals/sale_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from sales.models.sale_model import Sale


register_crud_signals(
    Sale,
    actions={
        'create': 'sale_created',
        'update': 'sale_updated',
        'delete': 'sale_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"Sale '{instance.name if instance.name else instance.id}' has been "
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'sale_id': instance.id,
        'sale_name': instance.name if instance.name else None,
        'created': created,
    }
)