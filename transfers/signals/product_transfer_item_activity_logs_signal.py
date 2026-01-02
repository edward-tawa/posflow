# transfers/signals/product_transfer_item_activity_logs_signal.py
from config.activity_log.crud_registry import register_crud_signals
from transfers.models.product_transfer_item_model import ProductTransferItem


register_crud_signals(
    ProductTransferItem,
    actions={
        'create': 'product_transfer_item_created',
        'update': 'product_transfer_item_updated',
        'delete': 'product_transfer_item_deleted'
    },
    get_description=lambda instance, created=False, deleted=False: (
        f"ProductTransferItem '{instance.name}' has been"
        f"{'created' if created else 'updated' if not deleted else 'deleted'}."
    ),
    get_metadata=lambda instance, created=False, deleted=False: {
        'product_transfer_item_id': instance.id,
        'product_transfer_item_name': instance.name,
        'created': created,
    }
)