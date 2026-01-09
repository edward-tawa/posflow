# transfers/signals/cash_transfer_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from transfers.models.cash_transfer_model import CashTransfer


register_crud_signals(
    CashTransfer,
    actions={
        'create': 'cash_transfer_created',
        'update': 'cash_transfer_updated',
        'delete': 'cash_transfer_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"CashTransfer '{instance.name if instance.name else instance.id}' has been"
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'cash_transfer_id': instance.id,
        'cash_transfer_name': instance.name if instance.name else None,
        'created': created,
    }
)