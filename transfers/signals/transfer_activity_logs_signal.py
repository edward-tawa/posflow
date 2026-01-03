# transfers/signals/transfer_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from transfers.models.transfer_model import Transfer


register_crud_signals(
    Transfer,
    actions={
        'create': 'transfer_created',
        'update': 'transfer_updated',
        'delete': 'transfer_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"Transfer '{instance.name}' has been"
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'transfer_id': instance.id,
        'transfer_name': instance.name,
        'created': created,
    }
)