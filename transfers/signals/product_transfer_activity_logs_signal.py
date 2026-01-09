# transfers/signals/product_transfer_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from transfers.models.product_transfer_model import ProductTransfer


register_crud_signals(
    ProductTransfer,
    actions={
        'create': 'product_transfer_created',
        'update': 'product_transfer_updated',
        'delete': 'product_transfer_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"ProductTransfer '{instance.transfer.reference_number if instance.transfer.reference_number else None}' has been"
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'product_transfer_id': instance.id,
        'product_transfer_reference': instance.transfer.reference_number if instance.transfer.reference_number else None,
        'created': created,
    }
)