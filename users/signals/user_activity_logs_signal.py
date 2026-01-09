# transactions/signals/transaction_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from users.models.user_model import User


register_crud_signals(
    User,
    actions={
        'create': 'user_created',
        'update': 'user_updated',
        'delete': 'user_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"Transaction '{instance.username if instance.username else instance.id}' has been"
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'transaction_id': instance.id,
        'transaction_name': instance.username if instance.username else None,
        'created': created,
    }
)