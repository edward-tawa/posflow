# transactions/signals/transaction_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from transactions.models.transaction_model import Transaction


register_crud_signals(
    Transaction,
    actions={
        'create': 'transaction_created',
        'update': 'transaction_updated',
        'delete': 'transaction_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"Transaction '{instance.name}' has been"
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'transaction_id': instance.id,
        'transaction_name': instance.name,
        'created': created,
    }
)