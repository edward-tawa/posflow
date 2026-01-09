# suppliers/signals/supplier_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from suppliers.models.supplier_model import Supplier

register_crud_signals(
    Supplier,
    actions={
        'create': 'supplier_created',
        'update': 'supplier_updated',
        'delete': 'supplier_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"Supplier '{instance.id if instance.id else None}' has been"
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'supplier_id': instance.id,
        'supplier_name': instance.id if instance.id else None,
        'created': created,
    }
)