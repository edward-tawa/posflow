# transactions/signals/transaction_item_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from transactions.models.transaction_item_model import TransactionItem


register_crud_signals(
    TransactionItem,
    actions={
        'create': 'transaction_item_created',
        'update': 'transaction_item_updated',
        'delete': 'transaction_item_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"TransactionItem '{instance.name if instance.name else instance.id}' has been"
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'transaction_item_id': instance.id,
        'transaction_item_name': instance.name if instance.name else None,
        'created': created,
    }
)