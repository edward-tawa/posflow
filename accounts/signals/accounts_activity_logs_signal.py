# accounts/signals/accounts_activity_logs_signal.py
from accounts.models.account_model import Account
from config.activity_log.crud_registry import register_crud_signals

register_crud_signals(
    Account,
    actions={
        'create': 'account_created',
        'update': 'account_updated',
        'delete': 'account_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"Account '{instance.name if instance.name else instance.id}' has been "
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'account_id': instance.id,
        'account_name': instance.name if instance.name else None,
        'created': created,
    }
)

